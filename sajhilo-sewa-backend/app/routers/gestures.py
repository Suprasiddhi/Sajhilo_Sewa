from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil

from app.database import get_db
from app import models, schemas
from app.auth_utils import get_current_active_user
from app.ml.config import VIDEO_ROOT, DATA_DIR

router = APIRouter(prefix="/gestures", tags=["gestures"])

@router.post("/", response_model=schemas.Gesture)
def create_gesture(
    gesture: schemas.GestureCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_gesture = models.Gesture(
        name=gesture.name,
        category=gesture.category
    )
    db.add(db_gesture)
    db.commit()
    db.refresh(db_gesture)

    for section in gesture.sections:
        db_section = models.GestureSection(
            gesture_id=db_gesture.id,
            title=section.title,
            description=section.description
        )
        db.add(db_section)
        db.commit()
        db.refresh(db_section)

        for media in section.media:
            db_media = models.Media(
                section_id=db_section.id,
                media_type=media.media_type,
                url=media.url
            )
            db.add(db_media)
    
    db.commit()
    db.refresh(db_gesture)
    return db_gesture

@router.get("/", response_model=List[schemas.Gesture])
def get_gestures(
    category: Optional[str] = "all", 
    db: Session = Depends(get_db)
):
    query = db.query(models.Gesture)
    if category and category != "all":
        query = query.filter(models.Gesture.category == category)
    
    return query.all()

@router.get("/{gesture_id}", response_model=schemas.Gesture)
def get_gesture(
    gesture_id: int, 
    db: Session = Depends(get_db)
):
    db_gesture = db.query(models.Gesture).filter(models.Gesture.id == gesture_id).first()
    if not db_gesture:
        raise HTTPException(status_code=404, detail="Gesture not found")
    return db_gesture

@router.put("/{gesture_id}", response_model=schemas.Gesture)
def update_gesture(
    gesture_id: int,
    gesture_update: schemas.GestureCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_gesture = db.query(models.Gesture).filter(models.Gesture.id == gesture_id).first()
    if not db_gesture:
        raise HTTPException(status_code=404, detail="Gesture not found")

    # Update main gesture
    db_gesture.name = gesture_update.name
    db_gesture.category = gesture_update.category
    
    # Clear old sections (and media via cascade="all, delete-orphan")
    db_gesture.sections = []
    db.flush()

    # Recreate sections and media
    for section_data in gesture_update.sections:
        db_section = models.GestureSection(
            gesture_id=db_gesture.id,
            title=section_data.title,
            description=section_data.description
        )
        db.add(db_section)
        db.flush() # Get section ID for media

        for media_data in section_data.media:
            db_media = models.Media(
                section_id=db_section.id,
                media_type=media_data.media_type,
                url=media_data.url
            )
            db.add(db_media)
    
    db.commit()
    db.refresh(db_gesture)
    return db_gesture

@router.delete("/{gesture_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gesture(
    gesture_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_gesture = db.query(models.Gesture).filter(models.Gesture.id == gesture_id).first()
    if not db_gesture:
        raise HTTPException(status_code=404, detail="Gesture not found")
    
    gesture_name = db_gesture.name
    
    # 1. Gather all file paths from Media before deleting the DB record
    media_files = []
    for section in db_gesture.sections:
        for media in section.media:
            if media.url and ("/uploads/" in media.url or "uploads/" in media.url):
                # Extract the filename from the URL
                filename = media.url.split('/')[-1]
                media_files.append(os.path.join("uploads", filename))
    
    # 2. Delete Physical Files
    for file_path in media_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Deleted upload file: {file_path}")
        except Exception as e:
            print(f"⚠️ Error deleting file {file_path}: {e}")
            
    # 3. Delete AI TRAINING folders
    paths_to_remove = [
        os.path.join(VIDEO_ROOT, gesture_name),
        os.path.join(DATA_DIR, gesture_name)
    ]
    for p in paths_to_remove:
        try:
            if os.path.exists(p):
                shutil.rmtree(p)
                print(f"🔥 Removed training folder: {p}")
        except Exception as e:
            print(f"⚠️ Error removing training folder {p}: {e}")

    # 4. Delete from Database
    db.delete(db_gesture)
    db.commit()
    return None

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user)
):
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return a mock URL for now (in a real app, this would be a public URL or served by FastAPI)
    return {"url": f"http://localhost:8000/{file_path}"}
