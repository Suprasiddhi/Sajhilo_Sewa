from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas
from app.auth_utils import get_current_active_user

router = APIRouter(prefix="/admin/stats", tags=["admin"])

@router.get("/", response_model=schemas.AdminStatsResponse)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # 1. Total User Count
    total_users = db.query(models.User).count()
    
    # 2. All Usernames
    usernames = [u.username for u in db.query(models.User).all()]
    
    # 3. Total Gesture Count
    total_gestures = db.query(models.Gesture).count()
    
    # 4. Latest 5 Gestures
    latest_gestures = db.query(models.Gesture).order_by(models.Gesture.created_at.desc()).limit(5).all()
    
    return {
        "total_users": total_users,
        "all_usernames": usernames,
        "total_gestures": total_gestures,
        "latest_gestures": latest_gestures
    }
