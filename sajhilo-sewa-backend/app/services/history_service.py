from sqlalchemy.orm import Session
from app.models import TranslationHistory
from app.schemas import TranslationHistoryCreate
from app.services.translator import translator_service

class HistoryService:
    def save_history_entry(self, db: Session, user_id: int, english_text: str, mode: str):
        """
        Translates English text to Nepali and saves to translation_history table.
        """
        if not english_text or not english_text.strip():
            return None
            
        nepali_text = translator_service.translate(english_text)
        
        db_entry = TranslationHistory(
            user_id=user_id,
            english_text=english_text.strip(),
            nepali_text=nepali_text,
            mode=mode
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry

    def get_user_history(self, db: Session, user_id: int, limit: int = 50):
        """
        Returns history for a specific user, sorted by date (newest first).
        """
        return db.query(TranslationHistory).filter(
            TranslationHistory.user_id == user_id
        ).order_by(TranslationHistory.created_at.desc()).limit(limit).all()

# Shared singleton
history_service = HistoryService()
