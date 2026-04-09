from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth_utils import get_current_active_user
from app.services.history_service import history_service

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("/", response_model=List[schemas.TranslationHistoryResponse])
def get_history(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get the translation history for the authenticated user.
    """
    return history_service.get_user_history(db, current_user.id, limit)
