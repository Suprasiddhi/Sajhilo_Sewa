"""
ml/dataset.py
──────────────
Handles all I/O between raw video files and model-ready numpy arrays.

Two public functions:
  process_video_dataset  — reads MP4/AVI/MOV videos → saves .npy keypoint files
  load_dataset           — reads .npy files → returns (X, y) numpy arrays

Expected video folder layout (VIDEO_ROOT):
    videos/
      hello/        clip1.mp4  clip2.mp4 ...
      thank_you/    vid1.mp4 ...
      water/        ...

After processing, DATA_DIR mirrors this structure with .npy files:
    data/
      hello/
        0/  0.npy 1.npy ... 29.npy   ← one sequence = 30 frames
        1/  ...
      thank_you/
        ...
"""
import os
import json

import cv2
import numpy as np
import mediapipe as mp

from app.ml.config import (
    SEQUENCE_LENGTH, NUM_JOINTS, COORDS,
    SLIDING_WINDOW, WINDOW_STRIDE,
    DATA_DIR, GESTURES,
)
from app.ml.preprocessing import extract_keypoints, run_mediapipe

# Keep one global hands detector for speed (avoid re-creating per frame)
try:
    _hands_ctx = mp.solutions.hands.Hands(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=1,
    )
    _MP_NEW_API = False
except AttributeError:
    _hands_ctx = None
    _MP_NEW_API = True

SUPPORTED_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm")


# ── Single video processing ───────────────────────────────────────────────────

def process_single_video(
    video_path: str,
    save_dir: str,
    seq_id: int,
    show_preview: bool = False,
) -> int:
    """
    Extract keypoint sequences from one video file using a sliding window.

    Steps:
      1. Read every frame and run MediaPipe to get 21 landmarks.
      2. Apply a sliding window of width SEQUENCE_LENGTH with step WINDOW_STRIDE.
      3. Save each clip as 30 individual .npy files inside a numbered subfolder.

    Returns: number of sequences saved.
    """
    os.makedirs(save_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  ⚠️  Cannot open: {video_path}")
        return 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS)
    print(f"  📹 {os.path.basename(video_path)} | {total_frames} frames @ {fps:.1f} fps")

    all_frames = []

    # ── Step 1: extract every frame's keypoints ───────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results   = run_mediapipe(image_rgb, _hands_ctx)
        all_frames.append(extract_keypoints(results))

    cap.release()

    if len(all_frames) < SEQUENCE_LENGTH:
        print(f"    ⚠️  Only {len(all_frames)} frames — need ≥{SEQUENCE_LENGTH}. Skipping.")
        return 0

    # ── Step 2: sliding window clipping ──────────────────────────
    stride           = WINDOW_STRIDE if SLIDING_WINDOW else SEQUENCE_LENGTH
    sequences_saved  = 0

    for start in range(0, len(all_frames) - SEQUENCE_LENGTH + 1, stride):
        clip     = all_frames[start: start + SEQUENCE_LENGTH]
        clip_dir = os.path.join(save_dir, str(seq_id + sequences_saved))
        os.makedirs(clip_dir, exist_ok=True)
        for f_idx, kp in enumerate(clip):
            np.save(os.path.join(clip_dir, str(f_idx)), kp)
        sequences_saved += 1

    return sequences_saved


# ── Full dataset processing ───────────────────────────────────────────────────

def process_video_dataset(
    video_root: str = None,
    data_dir: str   = None,
    gestures: list  = None,
    show_preview: bool = False,
) -> tuple[dict, list]:
    """
    Walk VIDEO_ROOT, process every video, and save .npy keypoint sequences.

    Args:
        video_root   : root folder containing one subfolder per gesture
        data_dir     : destination for .npy files (default: DATA_DIR)
        gestures     : list of gesture names to process; auto-detects if None
        show_preview : show OpenCV preview window (not supported in servers)

    Returns: (summary_dict, gestures_list)
    """
    video_root = video_root or __import__("app.ml.config", fromlist=["VIDEO_ROOT"]).VIDEO_ROOT
    data_dir   = data_dir   or DATA_DIR
    os.makedirs(data_dir, exist_ok=True)

    if gestures is None:
        gestures = sorted(
            d for d in os.listdir(video_root)
            if os.path.isdir(os.path.join(video_root, d))
        )
        print(f"Auto-detected {len(gestures)} gesture classes: {gestures}")

    summary = {}
    total   = 0

    print("\n" + "=" * 55)
    print("  PROCESSING VIDEO DATASET")
    print("=" * 55)

    for gesture in gestures:
        gesture_video_dir = os.path.join(video_root, gesture)
        gesture_data_dir  = os.path.join(data_dir,   gesture)

        if not os.path.isdir(gesture_video_dir):
            print(f"\n⚠️  Folder not found: {gesture_video_dir} — skipping")
            continue

        videos = sorted(
            f for f in os.listdir(gesture_video_dir)
            if f.lower().endswith(SUPPORTED_EXTENSIONS)
        )

        if not videos:
            print(f"\n⚠️  No videos in {gesture_video_dir} — skipping")
            continue

        print(f"\n[{gesture}] — {len(videos)} video(s)")
        gesture_seq_count = 0

        for video_file in videos:
            n = process_single_video(
                video_path   = os.path.join(gesture_video_dir, video_file),
                save_dir     = gesture_data_dir,
                seq_id       = gesture_seq_count,
                show_preview = show_preview,
            )
            gesture_seq_count += n
            print(f"    ✅ {video_file} → {n} sequences")

        summary[gesture] = gesture_seq_count
        total           += gesture_seq_count
        print(f"  → Total for [{gesture}]: {gesture_seq_count} sequences")

    print("\n" + "=" * 55)
    print(f"  DONE! Total sequences extracted: {total}")
    print("=" * 55)

    # Save summary so training can reload gesture list automatically
    with open(os.path.join(data_dir, "dataset_summary.json"), "w") as f:
        json.dump({"gestures": gestures, "sequences": summary}, f, indent=2)

    return summary, gestures


# ── Dataset loading ───────────────────────────────────────────────────────────

def load_dataset(
    data_dir: str = None,
    gestures: list = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load all saved .npy sequences into numpy arrays.

    Returns:
        X : (N, 30, 21, 3)  — raw landmark sequences
        y : (N,)            — integer class labels
    """
    data_dir = data_dir or DATA_DIR
    gestures = gestures or GESTURES

    X, y = [], []

    for label_idx, gesture in enumerate(gestures):
        gesture_dir = os.path.join(data_dir, gesture)
        if not os.path.isdir(gesture_dir):
            print(f"⚠️  Missing: {gesture_dir}")
            continue

        seq_folders = sorted(
            (d for d in os.listdir(gesture_dir)
             if os.path.isdir(os.path.join(gesture_dir, d)) and d.isdigit()),
            key=lambda x: int(x),
        )

        for seq_folder in seq_folders:
            seq_path = os.path.join(gesture_dir, seq_folder)
            frames   = []
            for frame_num in range(SEQUENCE_LENGTH):
                npy_path = os.path.join(seq_path, f"{frame_num}.npy")
                frames.append(
                    np.load(npy_path)
                    if os.path.exists(npy_path)
                    else np.zeros((NUM_JOINTS, COORDS), dtype=np.float32)
                )
            if len(frames) == SEQUENCE_LENGTH:
                X.append(frames)
                y.append(label_idx)

        print(f"  [{gesture}]: {len(seq_folders)} sequences loaded")

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)
    print(f"\n✅ Dataset ready: {X.shape[0]} total samples, {len(gestures)} classes")
    return X, y


# ── Gesture list helper ───────────────────────────────────────────────────────

def load_gestures_from_summary(data_dir: str = None) -> list | None:
    """Read the gesture list saved by process_video_dataset."""
    path = os.path.join(data_dir or DATA_DIR, "dataset_summary.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)["gestures"]
    return None

if __name__ == "__main__":
    from app.ml.config import VIDEO_ROOT
    process_video_dataset(video_root=VIDEO_ROOT, data_dir=DATA_DIR, gestures=GESTURES)