import os
import json
import cv2
import numpy as np
import mediapipe as mp
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models
from app.ml.config import (
    SEQUENCE_LENGTH, NUM_JOINTS, COORDS,
    SLIDING_WINDOW, WINDOW_STRIDE,
    GESTURES,
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
    _MP_NEW_API = False
except AttributeError:
    _hands_ctx = None
    _MP_NEW_API = True

SUPPORTED_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm")

def save_sequence_to_db(db: Session, gesture_id: int, sequence: list, is_augmented: bool = False):
    """Save a 30-frame sequence to the database as a single record."""
    # Flatten sequence to a list of 1890 floats
    flat_data = np.array(sequence).flatten().tolist()
    db_seq = models.GestureDataset(
        gesture_id=gesture_id,
        data=json.dumps(flat_data),
        is_augmented=is_augmented
    )
    db.add(db_seq)

def process_single_video(
    video_path: str,
    gesture_id: int,
    db: Session,
) -> int:
    """Extract keypoint sequences from one video and save to DB."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  ⚠️  Cannot open: {video_path}")
        return 0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"  📹 {os.path.basename(video_path)} | {total_frames} frames")

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
        print(f"    ⚠️  Only {len(all_frames)} frames — need ≥{SEQUENCE_LENGTH}. Skipping.")
        return 0

    stride = WINDOW_STRIDE if SLIDING_WINDOW else SEQUENCE_LENGTH
    sequences_saved = 0

    for start in range(0, len(all_frames) - SEQUENCE_LENGTH + 1, stride):
        clip = all_frames[start: start + SEQUENCE_LENGTH]
        save_sequence_to_db(db, gesture_id, clip)
        sequences_saved += 1
    
    db.commit()
    return sequences_saved

def process_video_dataset(
    video_root: str = None,
    gestures: list  = None,
) -> tuple[dict, list]:
    """Walk VIDEO_ROOT, process every video, and save to DB."""
    video_root = video_root or __import__("app.ml.config", fromlist=["VIDEO_ROOT"]).VIDEO_ROOT
    
    db = SessionLocal()
    try:
        if gestures is None:
            gestures = sorted(
                d for d in os.listdir(video_root)
                if os.path.isdir(os.path.join(video_root, d))
            )
            print(f"Auto-detected {len(gestures)} gesture classes: {gestures}")

        summary = {}
        total = 0

        print("\n" + "=" * 55)
        print("  PROCESSING VIDEO DATASET (DB MODE)")
        print("=" * 55)

        for gesture_name in gestures:
            # Find or create gesture in DB
            db_gesture = db.query(models.Gesture).filter(models.Gesture.name == gesture_name).first()
            if not db_gesture:
                print(f"Creating missing gesture in DB: {gesture_name}")
                db_gesture = models.Gesture(name=gesture_name, category="common")
                db.add(db_gesture)
                db.commit()
                db.refresh(db_gesture)

            gesture_video_dir = os.path.join(video_root, gesture_name)
            if not os.path.isdir(gesture_video_dir):
                continue

            videos = sorted(
                f for f in os.listdir(gesture_video_dir)
                if f.lower().endswith(SUPPORTED_EXTENSIONS)
            )

            if not videos:
                continue

            # Clear existing data for this gesture before re-processing
            # db.query(models.GestureDataset).filter(models.GestureDataset.gesture_id == db_gesture.id).delete()
            # db.commit()

            print(f"\n[{gesture_name}] — {len(videos)} video(s)")
            gesture_seq_count = 0

            for video_file in videos:
                n = process_single_video(
                    video_path = os.path.join(gesture_video_dir, video_file),
                    gesture_id = db_gesture.id,
                    db = db
                )
                gesture_seq_count += n
                print(f"    ✅ {video_file} → {n} sequences")

            summary[gesture_name] = gesture_seq_count
            total += gesture_seq_count
            print(f"  → Total for [{gesture_name}]: {gesture_seq_count} sequences")

        print("\n" + "=" * 55)
        print(f"  DONE! Total sequences extracted to DB: {total}")
        print("=" * 55)
        
        return summary, gestures
    finally:
        db.close()

def load_dataset(gestures: list = None) -> tuple[np.ndarray, np.ndarray]:
    """Load all saved sequences from DB into numpy arrays."""
    gestures = gestures or GESTURES
    db = SessionLocal()
    
    X, y = [], []
    try:
        for label_idx, gesture_name in enumerate(gestures):
            db_gesture = db.query(models.Gesture).filter(models.Gesture.name == gesture_name).first()
            if not db_gesture:
                print(f"⚠️  Missing gesture in DB: {gesture_name}")
                continue

            sequences = db.query(models.GestureDataset).filter(
                models.GestureDataset.gesture_id == db_gesture.id
            ).all()

            for seq in sequences:
                raw_data = json.loads(seq.data)
                # Reshape back to (30, 21, 3)
                frames = np.array(raw_data).reshape(SEQUENCE_LENGTH, NUM_JOINTS, COORDS)
                X.append(frames)
                y.append(label_idx)

            print(f"  [{gesture_name}]: {len(sequences)} sequences loaded from DB")

        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.int64)
        print(f"\n✅ Dataset ready: {X.shape[0]} total samples, {len(gestures)} classes")
        return X, y
    finally:
        db.close()

def load_gestures_from_summary() -> list | None:
    """Return the list of gestures that have data in the DB."""
    db = SessionLocal()
    try:
        # Get all gesture IDs that have at least one sequence
        gesture_ids = db.query(models.GestureDataset.gesture_id).distinct().all()
        gesture_ids = [r[0] for r in gesture_ids]
        
        if not gesture_ids:
            return None
            
        gestures = db.query(models.Gesture.name).filter(models.Gesture.id.in_(gesture_ids)).all()
        return sorted([r[0] for r in gestures])
    finally:
        db.close()

if __name__ == "__main__":
    process_video_dataset()

if __name__ == "__main__":
    from app.ml.config import VIDEO_ROOT
    process_video_dataset(video_root=VIDEO_ROOT, data_dir=DATA_DIR, gestures=GESTURES)