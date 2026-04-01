"""
ml/dataset.py
──────────────
Handles all I/O between raw video files and model-ready numpy arrays.
This version only uses the Local Filesystem for Training Data storage.
"""
import os
import json
import cv2
import numpy as np
import mediapipe as mp

from app.ml.config import (
    SEQUENCE_LENGTH, NUM_JOINTS, COORDS,
    SLIDING_WINDOW, WINDOW_STRIDE,
    DATA_DIR, GESTURES, VIDEO_ROOT
)
from app.ml.preprocessing import extract_keypoints, run_mediapipe

# Keep one global hands detector for speed
try:
    _hands_ctx = mp.solutions.hands.Hands(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=1,
    )
except AttributeError:
    _hands_ctx = None

SUPPORTED_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm")

# ── Single video processing ───────────────────────────────────────────────────

def process_single_video(
    video_path: str,
    gesture_name: str,
    save_to_fs: bool = True,
) -> int:
    """
    Extract keypoint sequences from one video file.
    Saves to: app/data/{gesture_name}/{sequence_index}/{frame_index}.npy
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  ⚠️  Cannot open: {video_path}")
        return 0

    all_frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results   = run_mediapipe(image_rgb, _hands_ctx)
        all_frames.append(extract_keypoints(results))
    cap.release()

    if len(all_frames) < SEQUENCE_LENGTH:
        return 0

    gesture_data_root = os.path.join(DATA_DIR, gesture_name)
    os.makedirs(gesture_data_root, exist_ok=True)
    
    # Check existing sequence indices to not overwrite
    existing_indices = [int(d) for d in os.listdir(gesture_data_root) if d.isdigit()]
    start_idx = max(existing_indices) + 1 if existing_indices else 0

    stride = WINDOW_STRIDE if SLIDING_WINDOW else SEQUENCE_LENGTH
    sequences_saved = 0
    
    for start in range(0, len(all_frames) - SEQUENCE_LENGTH + 1, stride):
        clip = all_frames[start: start + SEQUENCE_LENGTH]
        
        if save_to_fs:
            seq_dir = os.path.join(gesture_data_root, str(start_idx + sequences_saved))
            os.makedirs(seq_dir, exist_ok=True)
            for f_idx, kp in enumerate(clip):
                np.save(os.path.join(seq_dir, f"{f_idx}.npy"), kp)
        
        sequences_saved += 1

    return sequences_saved


# ── Full dataset processing ───────────────────────────────────────────────────

def process_video_dataset(video_root=VIDEO_ROOT):
    """
    Walks VIDEO_ROOT (local folders) and processes every video found.
    """
    if not os.path.exists(video_root):
        print(f"❌ Error: {video_root} not found.")
        return {}, []

    # Detect gestures from folder names inside VIDEO_ROOT
    gestures = sorted([
        d for d in os.listdir(video_root)
        if os.path.isdir(os.path.join(video_root, d))
    ])

    summary = {}
    total_seq = 0

    for gesture in gestures:
        gesture_dir = os.path.join(video_root, gesture)
        videos = [f for f in os.listdir(gesture_dir) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
        
        if not videos:
            continue

        print(f"Processing gesture: [{gesture}] ({len(videos)} videos)...")
        gesture_seq_count = 0
        for video_file in videos:
            n = process_single_video(
                video_path=os.path.join(gesture_dir, video_file),
                gesture_name=gesture
            )
            gesture_seq_count += n
        
        summary[gesture] = gesture_seq_count
        total_seq += gesture_seq_count

    # Save summary for training orchestration
    with open(os.path.join(DATA_DIR, "dataset_summary.json"), "w") as f:
        json.dump({"gestures": gestures, "sequences": summary}, f, indent=2)

    print(f"\n✅ Finished processing {len(gestures)} gestures.")
    print(f"   Total local sequences extracted: {total_seq}")
    return summary, gestures


# ── Dataset loading (Filesystem Only) ──────────────────────────────────────────

def load_dataset(gestures: list = None) -> tuple[np.ndarray, np.ndarray]:
    """
    Loads all sequences previously extracted to DATA_DIR (app/data/).
    Expected structure: app/data/{gesture}/{index}/0.npy ... 29.npy
    """
    if gestures is None:
        gestures = [
            d for d in os.listdir(DATA_DIR)
            if os.path.isdir(os.path.join(DATA_DIR, d))
        ]
        gestures = sorted(gestures)

    X, y = [], []
    gesture_to_idx = {name: i for i, name in enumerate(gestures)}

    print(f"Loading local dataset from: {DATA_DIR}")

    for gesture in gestures:
        gesture_path = os.path.join(DATA_DIR, gesture)
        if not os.path.exists(gesture_path):
            continue

        # Get all sequence index folders (0, 1, 2...)
        seq_dirs = [d for d in os.listdir(gesture_path) if d.isdigit()]
        
        gesture_count = 0
        for seq_id in seq_dirs:
            seq_path = os.path.join(gesture_path, seq_id)
            
            # Load frames 0..29
            frames = []
            valid_seq = True
            for f_idx in range(SEQUENCE_LENGTH):
                f_path = os.path.join(seq_path, f"{f_idx}.npy")
                if not os.path.exists(f_path):
                    valid_seq = False
                    break
                frames.append(np.load(f_path))
            
            if valid_seq:
                X.append(np.array(frames, dtype=np.float32))
                y.append(gesture_to_idx[gesture])
                gesture_count += 1
        
        print(f"  [{gesture}]: {gesture_count} sequences loaded")

    if not X:
        print("⚠️  No data found in app/data/. Run /api/ml/process-videos first.")
        return np.array([]), np.array([])
        
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)
    print(f"✅ Loaded {X.shape[0]} samples total.")
    return X, y

def load_gestures_from_summary(data_dir: str = None) -> list | None:
    path = os.path.join(data_dir or DATA_DIR, "dataset_summary.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)["gestures"]
    return None

if __name__ == "__main__":
    process_video_dataset()