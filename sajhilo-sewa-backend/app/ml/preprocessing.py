"""
ml/preprocessing.py
────────────────────
Everything that touches raw pixels or raw keypoints before they enter a model.

Responsibilities:
  1. MediaPipe hand landmark extraction  (extract_keypoints)
  2. Input format conversion per model   (preprocess_for_models)
  3. Keypoint augmentation               (augment_dataset)
"""
import os
import urllib.request

import cv2
import mediapipe as mp
import numpy as np

from app.ml.config import NUM_JOINTS, COORDS, SEQUENCE_LENGTH

# ── MediaPipe API detection ───────────────────────────────────────────────────

try:
    _mp_hands   = mp.solutions.hands
    _mp_drawing = mp.solutions.drawing_utils
    _MP_NEW_API = False
except AttributeError:
    from mediapipe.tasks import python as _mp_python
    from mediapipe.tasks.python import vision as _mp_vision
    # New MediaPipe Tasks API uses mp.Image
    _MP_Image = mp.Image
    _MP_ImageFormat = mp.ImageFormat

    _MODEL_PATH = "hand_landmarker.task"
    if not os.path.exists(_MODEL_PATH):
        print("Downloading MediaPipe hand landmark model (~8MB)...")
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
            "hand_landmarker/float16/latest/hand_landmarker.task",
            _MODEL_PATH,
        )

    _base_options = _mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
    _hand_options = _mp_vision.HandLandmarkerOptions(
        base_options=_base_options,
        num_hands=1,
        min_hand_detection_confidence=0.4,
        min_hand_presence_confidence=0.4,
        min_tracking_confidence=0.4,
    )
    _HandLandmarker = _mp_vision.HandLandmarker
    _MP_NEW_API = True

    # Shared Hand detector singleton
    _hand_detector = _HandLandmarker.create_from_options(_hand_options)


# ── Landmark extraction ───────────────────────────────────────────────────────

def extract_keypoints(results) -> np.ndarray:
    """
    Pull 21 (x,y,z) landmarks from a MediaPipe result object.

    Works with both the legacy solutions API and the newer Tasks API.
    Returns zeros (shape 21×3) when no hand is detected so every frame
    has the same shape.
    """
    if _MP_NEW_API:
        if results and results.hand_landmarks:
            hand = results.hand_landmarks[0]
            return np.array([[lm.x, lm.y, lm.z] for lm in hand], dtype=np.float32)
    else:
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            return np.array(
                [[lm.x, lm.y, lm.z] for lm in hand.landmark], dtype=np.float32
            )
    return np.zeros((NUM_JOINTS, COORDS), dtype=np.float32)


def normalize_keypoints(landmarks: np.ndarray) -> np.ndarray:
    """
    Standardize the hand scale and position.
    1. Center the hand by making the wrist (index 0) the origin (0,0,0).
    2. Scale the hand so that all landmarks fit within a consistent range.
    """
    if np.all(landmarks == 0):
        return landmarks

    # Copy to avoid modifying original
    landmarks = landmarks.copy()

    # 1. Centering (Relative to wrist)
    wrist = landmarks[0]
    landmarks = landmarks - wrist

    # 2. Scaling
    # Find the maximum absolute value among remaining coordinates
    max_val = np.abs(landmarks).max()
    if max_val > 0:
        landmarks = landmarks / max_val

    return landmarks.astype(np.float32)


def run_mediapipe(image_rgb: np.ndarray, hands_detector):
    """Helper: dispatch to old or new MediaPipe API."""
    # Resize to square to suppress MediaPipe warnings about non-square ROIs.
    # Normalized landmarks (0-1) are mathematically identical whether the image
    # is squashed to a square or not, but MediaPipe's internal calculator
    # expects a square ROI or explicit dimensions to avoid warnings.
    h, w = image_rgb.shape[:2]
    if h != w:
        size = max(h, w)
        image_rgb = cv2.resize(image_rgb, (size, size))

    if _MP_NEW_API:
        mp_image = _MP_Image(
            image_format=_MP_ImageFormat.SRGB, data=image_rgb
        )
        return _hand_detector.detect(mp_image)
    else:
        return hands_detector.process(image_rgb)


# ── Per-model format conversion ───────────────────────────────────────────────

def preprocess_for_models(X: np.ndarray) -> dict:
    """
    Convert raw keypoints into the input format each model expects.

    Args:
        X : (N, T=30, V=21, C=3) — raw landmark sequences

    Returns dict with:
        'tcn'    → (N, 63, 30)   — features-first for Conv1d
        'bilstm' → (N, 30, 63)   — time-first for LSTM
        'stgcn'  → (N, 3, 30, 21)— coords × time × joints for Conv2d
    """
    N, T, V, C = X.shape
    return {
        "tcn":    X.reshape(N, T, V * C).transpose(0, 2, 1),  # (N,63,30)
        "bilstm": X.reshape(N, T, V * C),                      # (N,30,63)
        "stgcn":  X.transpose(0, 3, 1, 2),                     # (N,3,30,21)
    }


# ── Augmentation ──────────────────────────────────────────────────────────────

def _augment_sequence(seq: np.ndarray) -> np.ndarray:
    """
    Apply random spatial and temporal perturbations to a single sequence.

    Augmentations (each applied probabilistically):
      1. Gaussian jitter      — small position noise
      2. Scale                — zoom in/out around hand centre
      3. 2D rotation          — rotate hand in XY plane ±20°
      4. Time warp            — stretch or squash the sequence
      5. Horizontal flip      — mirror left-right
      6. Frame dropout        — randomly zero out up to 3 frames
    """
    seq = seq.copy()
    T, V, C = seq.shape

    if np.random.rand() < 0.8:
        seq += np.random.normal(0, 0.01, seq.shape).astype(np.float32)

    if np.random.rand() < 0.7:
        scale  = np.random.uniform(0.85, 1.15)
        center = seq.mean(axis=(0, 1), keepdims=True)
        seq    = (seq - center) * scale + center

    if np.random.rand() < 0.6:
        angle        = np.random.uniform(-20, 20) * np.pi / 180
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        xy           = seq[:, :, :2].copy()
        seq[:, :, 0] = xy[:, :, 0] * cos_a - xy[:, :, 1] * sin_a
        seq[:, :, 1] = xy[:, :, 0] * sin_a + xy[:, :, 1] * cos_a

    if np.random.rand() < 0.5:
        orig_t  = np.linspace(0, 1, T)
        new_len = max(T, int(T * np.random.uniform(0.8, 1.2)))
        new_t   = np.linspace(0, 1, new_len)
        warped  = np.zeros_like(seq)
        for v in range(V):
            for c in range(C):
                warped[:, v, c] = np.interp(
                    orig_t, new_t,
                    np.interp(np.linspace(0, 1, new_len), np.linspace(0, 1, T), seq[:, v, c])
                    if new_len != T else seq[:, v, c],
                )
        seq = warped.astype(np.float32)

    if np.random.rand() < 0.4:
        seq[:, :, 0] = 1.0 - seq[:, :, 0]

    if np.random.rand() < 0.4:
        drop = np.random.choice(T, size=min(3, T // 5), replace=False)
        seq[drop] = 0.0

    return seq.astype(np.float32)


def augment_dataset(
    X: np.ndarray, y: np.ndarray, multiplier: int = 5
) -> tuple[np.ndarray, np.ndarray]:
    """
    Expand the training set by generating `multiplier` augmented copies
    of every sequence, then shuffling the combined dataset.

    Returns: (X_out, y_out) both shuffled.
    """
    X_list, y_list = [X], [y]
    for _ in range(multiplier):
        X_list.append(np.stack([_augment_sequence(s) for s in X]))
        y_list.append(y)

    X_out = np.concatenate(X_list, axis=0)
    y_out = np.concatenate(y_list, axis=0)
    idx   = np.random.permutation(len(X_out))
    print(f"  Dataset expanded: {len(X)} → {len(X_out)} samples ({multiplier + 1}×)")
    return X_out[idx], y_out[idx]