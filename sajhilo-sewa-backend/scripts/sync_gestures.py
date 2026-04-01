import os
from app.database import SessionLocal
from app.models import Gesture

def sync_gestures():
    db = SessionLocal()
    try:
        # 1. Check video folders
        v_path = 'videos/gestures'
        if not os.path.exists(v_path):
            print(f"Error: {v_path} does not exist.")
            return

        v_gestures = [d for d in os.listdir(v_path) if os.path.isdir(os.path.join(v_path, d))]
        print(f"Folders in videos/gestures: {v_gestures}")

        # 2. Check DB
        db_gestures = {g.name: g for g in db.query(Gesture).all()}
        print(f"Gestures in DB: {list(db_gestures.keys())}")

        # 3. Find missing
        missing = set(v_gestures) - set(db_gestures.keys())
        print(f"Missing in DB: {missing}")

        for m in missing:
            print(f"Adding {m} to DB...")
            new_g = Gesture(name=m, category='common')
            db.add(new_g)
        
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_gestures()
