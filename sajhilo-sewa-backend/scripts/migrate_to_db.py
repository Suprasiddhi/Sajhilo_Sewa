import os
import json
import numpy as np
from sqlalchemy.orm import Session
import sys

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models
from app.ml.config import DATA_DIR, SEQUENCE_LENGTH, NUM_JOINTS, COORDS

def migrate():
    db = SessionLocal()
    try:
        print(f"Starting migration from {DATA_DIR} to Database...")
        
        gestures = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
        
        total_sequences = 0
        
        for gesture_name in gestures:
            gesture_path = os.path.join(DATA_DIR, gesture_name)
            
            # Find or create gesture in DB
            db_gesture = db.query(models.Gesture).filter(models.Gesture.name == gesture_name).first()
            if not db_gesture:
                print(f"Creating gesture: {gesture_name}")
                db_gesture = models.Gesture(name=gesture_name, category="common")
                db.add(db_gesture)
                db.commit()
                db.refresh(db_gesture)
            
            # Find sequence folders (0, 1, 2...)
            seq_folders = [d for d in os.listdir(gesture_path) if os.path.isdir(os.path.join(gesture_path, d)) and d.isdigit()]
            
            print(f"Processing [{gesture_name}]: {len(seq_folders)} sequences")
            
            for seq_folder in seq_folders:
                seq_path = os.path.join(gesture_path, seq_folder)
                frames = []
                for frame_num in range(SEQUENCE_LENGTH):
                    npy_path = os.path.join(seq_path, f"{frame_num}.npy")
                    if os.path.exists(npy_path):
                        frames.append(np.load(npy_path))
                    else:
                        frames.append(np.zeros((NUM_JOINTS, COORDS), dtype=np.float32))
                
                # Flatten and save to DB
                flat_data = np.array(frames).flatten().tolist()
                db_seq = models.GestureDataset(
                    gesture_id=db_gesture.id,
                    data=json.dumps(flat_data),
                    is_augmented=False
                )
                db.add(db_seq)
                total_sequences += 1
            
            db.commit()
            print(f"  ✅ Completed [{gesture_name}]")
            
        print(f"\nMigration finished! Total sequences moved: {total_sequences}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
