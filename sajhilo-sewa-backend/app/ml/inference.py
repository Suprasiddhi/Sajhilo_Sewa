"""
ml/inference.py
────────────────
GestureRecognizer — the live inference engine used by the WebSocket handler.

How it works:
  1. Receives one video frame at a time (as a numpy array or base64 string).
  2. Runs MediaPipe to extract 21 hand landmarks.
  3. Appends the landmarks to a rolling buffer of 30 frames.
  4. Once the buffer is full, runs the ensemble (TCN + BiLSTM + ST-GCN).
  5. Returns the predicted gesture and confidence.
  6. The buffer shifts by 1 frame on each call → continuous prediction.

This class is instantiated ONCE at startup and reused for every WebSocket
connection — model loading is expensive, so we share the loaded weights.
"""
import base64
import io
import json
import os

import cv2
import mediapipe as mp
import numpy as np
import torch
import logging

# Suppress MediaPipe/TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'
from PIL import Image

from app.ml.config import (
    SEQUENCE_LENGTH, NUM_JOINTS, COORDS,
    WEIGHTS_DIR, CONFIDENCE_THRESHOLD, DEVICE, GESTURES,
)
from app.ml.models.tcn_model    import TCNModel
from app.ml.models.bilstm_model import BiLSTMModel
from app.ml.models.stgcn_model  import STGCNModel, build_adjacency_matrix
from app.ml.train               import TCNTrainer, BiLSTMTrainer, STGCNTrainer
from app.ml.ensemble            import EnsembleVoter
from app.ml.preprocessing       import extract_keypoints, preprocess_for_models
from app.ml.models.alphabet_model import AlphabetModel

# MediaPipe — legacy solutions API preferred for speed
try:
    _mp_hands = mp.solutions.hands
    _MP_NEW_API = False
except AttributeError:
    _MP_NEW_API = True


class GestureRecognizer:
    """
    Stateful inference engine.

    One instance is created at app startup and shared across all
    WebSocket connections.  Per-connection state (the frame buffer)
    is isolated via client_id.
    """

    def __init__(self):
        self.device   = DEVICE
        self.gestures = self._load_gesture_list()
        self.num_classes = len(self.gestures)
        self.A        = build_adjacency_matrix()

        # Per-connection rolling frame buffers  {client_id: list}
        self._buffers: dict[str, list] = {}

        # Sentence accumulation state
        self._sentences: dict[str, list[str]] = {}
        self._stability_counters: dict[str, int] = {}
        self._last_raw_prediction: dict[str, str] = {}
        self._last_stable_gesture: dict[str, str] = {}
        self._stability_threshold = 5  # increased for stability

        # Frame skipping (only run heavy ML every N frames)
        self._inference_frequency = 2
        self._inference_skip_counters: dict[str, int] = {}
        self._last_results: dict[str, dict] = {}

        # MediaPipe detector — one shared instance
        if not _MP_NEW_API:
            self._hands = _mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        else:
            self._hands = None   # new API creates context per-call

        # Load ML models
        self.ensemble = self._load_ensemble()
        print(f"✅ GestureRecognizer ready | device={self.device} | classes={self.num_classes}")

    # ── Setup helpers ─────────────────────────────────────────────

    def _load_gesture_list(self) -> list:
        """Load gesture list from ensemble_weights.json, falling back to config."""
        path = os.path.join(WEIGHTS_DIR, "ensemble_weights.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)["gestures"]
        print("⚠️  ensemble_weights.json not found — using GESTURES from config.py")
        return GESTURES

    def _load_ensemble(self) -> EnsembleVoter | None:
        """
        Load saved weights for all 3 models.
        Returns None (gracefully) if weights are missing — useful before
        training is run for the first time.
        """
        required = ["tcn_best.pth", "bilstm_best.pth", "stgcn_best.pth"]
        for fname in required:
            if not os.path.exists(os.path.join(WEIGHTS_DIR, fname)):
                print(f"⚠️  Weight file missing: {fname} — predictions disabled until training.")
                return None

        tcn    = TCNTrainer(TCNModel(63, self.num_classes))
        bilstm = BiLSTMTrainer(BiLSTMModel(63, 256, num_classes=self.num_classes))
        stgcn  = STGCNTrainer(STGCNModel(3, self.num_classes, self.A))

        tcn.load_best()
        bilstm.load_best()
        stgcn.load_best()

        ensemble = EnsembleVoter(tcn, bilstm, stgcn, self.gestures)

        # Load calibrated weights if available
        meta_path = os.path.join(WEIGHTS_DIR, "ensemble_weights.json")
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
            if "weights" in meta:
                ensemble.weights = np.array(meta["weights"], dtype=np.float32)
                print(f"  Ensemble weights loaded: {ensemble.weights}")

        return ensemble

    # ── Per-connection buffer management ─────────────────────────

    def init_client(self, client_id: str):
        """Create a fresh frame buffer and sentence state for a new WebSocket connection."""
        self._buffers[client_id] = []
        self._sentences[client_id] = []
        self._stability_counters[client_id] = 0
        self._last_raw_prediction[client_id] = ""
        self._last_stable_gesture[client_id] = ""
        self._inference_skip_counters[client_id] = 0
        self._last_results[client_id] = {"success": False, "message": "Buffering…"}

    def remove_client(self, client_id: str):
        """Clean up buffers and sentence state when client disconnects."""
        self._buffers.pop(client_id, None)
        self._sentences.pop(client_id, None)
        self._stability_counters.pop(client_id, None)
        self._last_raw_prediction.pop(client_id, None)
        self._last_stable_gesture.pop(client_id, None)
        self._inference_skip_counters.pop(client_id, None)
        self._last_results.pop(client_id, None)

    # ── Frame processing ──────────────────────────────────────────

    def _extract_from_frame(self, frame: np.ndarray) -> np.ndarray:
        """Run MediaPipe on one RGB frame, return (21,3) landmarks."""
        rgb = frame  # PIL decode already provides RGB

        if _MP_NEW_API:
            from app.ml.preprocessing import run_mediapipe
            results = run_mediapipe(rgb, None)
        else:
            results = self._hands.process(rgb)

        return extract_keypoints(results)   # (21, 3)

    def process_frame(self, client_id: str, frame_input) -> dict:
        """
        Accept one frame, update the rolling buffer, and return a prediction.
        """
        # ── Ensure buffer exists ──────────────────────────────────
        if client_id not in self._buffers:
            self.init_client(client_id)

        # ── Decode frame ──────────────────────────────────────────
        if isinstance(frame_input, str):
            if "," in frame_input:
                frame_input = frame_input.split(",")[1]
            try:
                img_bytes = base64.b64decode(frame_input)
                pil_img   = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                frame     = np.array(pil_img)
            except Exception as e:
                print(f"❌ Base64 decode error: {e}")
                return {"success": False, "message": "Corrupt frame data."}
        else:
            frame = frame_input

        # ── Extract landmarks ─────────────────────────────────────
        landmarks = self._extract_from_frame(frame)   # (21, 3)

        # DEBUG: Check if hand was detected
        if np.all(landmarks == 0):
             if self._inference_skip_counters[client_id] % 20 == 0:
                print(f"⚠️  [ID:{client_id}] No hand detected.")

        # ── Update rolling buffer ─────────────────────────────────
        buf = self._buffers[client_id]
        buf.append(landmarks)
        if len(buf) > SEQUENCE_LENGTH:
            buf.pop(0)

        buf_len = len(buf)

        if buf_len < SEQUENCE_LENGTH:
            return {
                "success": False,
                "message": f"Buffering frames…",
                "buffer_progress": f"{buf_len}/{SEQUENCE_LENGTH}",
            }

        if self.ensemble is None:
            return {
                "success": False,
                "message": "Models not loaded.",
                "buffer_progress": f"{buf_len}/{SEQUENCE_LENGTH}",
            }

        # ── Run ensemble prediction ───────────────────────────────
        sequence  = np.array(buf, dtype=np.float32)
        
        # 🧪 SAFETY CHECK: Skip inference if buffer is entirely empty
        if np.all(sequence == 0):
             res = {
                "success": False,
                "message": "No hand detected. Awaiting gestures...",
                "buffer_progress": f"{buf_len}/{SEQUENCE_LENGTH}",
                "sentence": " ".join(self._sentences[client_id])
            }
             self._last_results[client_id] = res
             return res

        X         = sequence[np.newaxis]
        inputs    = preprocess_for_models(X)

        self._inference_skip_counters[client_id] += 1
        if (self._inference_skip_counters[client_id] % self._inference_frequency != 0 and 
            self._last_raw_prediction.get(client_id)):
            return self._last_results[client_id]

        result = self.ensemble.predict_single(inputs)
        raw_gesture = result["gesture"]
        confidence  = result["confidence"]

        if self._inference_skip_counters[client_id] % 15 == 0:
            print(f"🔍 [Inference] Raw: {raw_gesture} ({confidence:.0%})")

        # ── Stability & Sentence Accumulation ─────────────────────
        if confidence < CONFIDENCE_THRESHOLD:
            self._stability_counters[client_id] = 0
            self._last_raw_prediction[client_id] = ""
            
            res = {
                "success": False,
                "gesture": raw_gesture,
                "confidence": confidence,
                "message": f"Low confidence ({confidence:.0%})",
                "buffer_progress": f"{buf_len}/{SEQUENCE_LENGTH}",
                "sentence": " ".join(self._sentences[client_id])
            }
            self._last_results[client_id] = res
            return res

        if raw_gesture == self._last_raw_prediction.get(client_id):
            self._stability_counters[client_id] += 1
        else:
            self._stability_counters[client_id] = 1
            self._last_raw_prediction[client_id] = raw_gesture

        is_final = False
        if (self._stability_counters[client_id] >= self._stability_threshold and 
            raw_gesture != self._last_stable_gesture.get(client_id)):
            
            if raw_gesture == 'ok':
                is_final = True
                print("🏁 Session end gesture detected: 'ok'")
            else:
                self._sentences[client_id].append(raw_gesture)
                self._last_stable_gesture[client_id] = raw_gesture
                print(f"✨ Recognised stable word: {raw_gesture}")

        final_result = {
            "success":        True,
            "gesture":        raw_gesture,
            "confidence":     confidence,
            "sentence":       " ".join(self._sentences[client_id]),
            "is_final":       is_final,
            "all_probs":      result["all_probs"],
            "model_votes":    result["model_votes"],
            "buffer_progress": f"{buf_len}/{SEQUENCE_LENGTH}",
        }
        self._last_results[client_id] = final_result
        return final_result

    def clear_sentence(self, client_id: str):
        """Clear the accumulated sentence and reset stability state."""
        if client_id in self._sentences:
            self._sentences[client_id] = []
            self._last_stable_gesture[client_id] = ""
            self._stability_counters[client_id] = 0
            self._last_raw_prediction[client_id] = ""

    def reset_buffer(self, client_id: str):
        """Manually clear a client's frame buffer."""
        self._buffers[client_id] = []


# ── Global singleton ──────────────────────────────────────────────────────────
# Instantiated once when the module is first imported.
recognizer = GestureRecognizer()

class AlphabetRecognizer:
    def __init__(self):
        self.device = DEVICE
        self.labels = self._load_labels()
        self.num_classes = len(self.labels)
        from app.ml.models.alphabet_model import AlphabetModel
        self.model = AlphabetModel(num_classes=self.num_classes).to(self.device)
        self._load_model()
        self._stability_counters = {}
        self._last_raw_prediction = {}
        self._stability_threshold = 5  # increased for stability
        self._sentences = {}
        
        # Use consistent MediaPipe initialization
        if not _MP_NEW_API:
            self._hands = _mp_hands.Hands(
                static_image_mode=False, 
                max_num_hands=1, 
                min_detection_confidence=0.5
            )
        else:
            self._hands = None

    def init_client(self, client_id: str):
        """Initialize per-client state for alphabet recognition."""
        self._sentences[client_id] = ""
        self._last_raw_prediction[client_id] = ""
        self._stability_counters[client_id] = 0

    def remove_client(self, client_id: str):
        """Clean up per-client state on disconnect."""
        self._sentences.pop(client_id, None)
        self._last_raw_prediction.pop(client_id, None)
        self._stability_counters.pop(client_id, None)

    def _load_labels(self):
        import os, json
        path = os.path.join(WEIGHTS_DIR, "alphabet_labels.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["del", "nothing", "space"]

    def _load_model(self):
        import os, torch
        path = os.path.join(WEIGHTS_DIR, "alphabet_best.pth")
        if os.path.exists(path): 
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            print(f"✅ Alphabet model weights loaded from {path}")
        else:
            print(f"⚠️  Alphabet weights not found at {path}. Have you run the trainer?")
        self.model.eval()

    def process_frame(self, client_id, frame_input):
        import numpy as np, cv2, base64, io, torch
        from app.ml.preprocessing import extract_keypoints, normalize_keypoints
        
        # Ensure client is initialized
        if client_id not in self._sentences:
            self.init_client(client_id)
        
        # ── Decode frame ──────────────────────────────────────────
        if isinstance(frame_input, str):
            if ',' in frame_input: frame_input = frame_input.split(',')[1]
            img_bytes = base64.b64decode(frame_input)
            pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            frame = np.array(pil_img)
        else:
            frame = frame_input

        # ── Extract landmarks ─────────────────────────────────────
        rgb = frame  # RGB from PIL

        if _MP_NEW_API:
            from app.ml.preprocessing import run_mediapipe
            results = run_mediapipe(rgb, None)
        else:
            results = self._hands.process(rgb)
        
        landmarks = extract_keypoints(results) 
        if np.all(landmarks == 0):
            return {'success': False, 'gesture': 'No hand', 'sentence': self._sentences[client_id]}

        # ── Normalization (VERY IMPORTANT for MLP) ──────────────────
        normalized_landmarks = normalize_keypoints(landmarks)
        
        with torch.no_grad():
            from app.ml.models.alphabet_model import AlphabetModel
            out = self.model(torch.FloatTensor(normalized_landmarks.flatten()).unsqueeze(0).to(self.device))
            probs = torch.softmax(out, dim=1).cpu().numpy()[0]
            idx = np.argmax(probs)
            label, conf = self.labels[idx], float(probs[idx])
        if conf > 0.45:
            if label == self._last_raw_prediction.get(client_id):
                self._stability_counters[client_id] += 1
            else:
                self._stability_counters[client_id] = 1
                self._last_raw_prediction[client_id] = label

            is_final = False
            if self._stability_counters[client_id] == self._stability_threshold:
                if label == 'space':
                    self._sentences[client_id] += ' '
                elif label == 'del':
                    self._sentences[client_id] = self._sentences[client_id][:-1]
                elif label == 'thumbs_up':
                    is_final = True
                    print("🏁 Session end gesture detected: 'thumbs_up'")
                elif label != 'nothing':
                    self._sentences[client_id] += label
                print(f"✨ Typed Letter: {label} | Current Word: {self._sentences[client_id]}")
        else:
             self._stability_counters[client_id] = 0
             is_final = False
        
        return {
            'success': True, 
            'gesture': label, 
            'confidence': conf, 
            'sentence': self._sentences[client_id],
            'is_final': is_final
        }

    def clear_sentence(self, client_id: str):
        """Clear the accumulated word and reset stability state."""
        self._sentences[client_id] = ""
        self._last_raw_prediction[client_id] = ""
        self._stability_counters[client_id] = 0

alphabet_recognizer = AlphabetRecognizer()
