from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Gesture(Base):
    __tablename__ = "gestures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True) # e.g., 'alphabets', 'numbers', 'words', 'common'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sections = relationship("GestureSection", back_populates="gesture", cascade="all, delete-orphan")
    training_data = relationship("TrainingData", back_populates="gesture", cascade="all, delete-orphan")

class GestureSection(Base):
    __tablename__ = "gesture_sections"

    id = Column(Integer, primary_key=True, index=True)
    gesture_id = Column(Integer, ForeignKey("gestures.id"))
    title = Column(String)
    description = Column(Text, nullable=True)

    gesture = relationship("Gesture", back_populates="sections")
    media = relationship("Media", back_populates="section", cascade="all, delete-orphan")

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("gesture_sections.id"))
    media_type = Column(String) # 'video' or 'image'
    url = Column(String)

    section = relationship("GestureSection", back_populates="media")

class TrainingData(Base):
    __tablename__ = "training_data"

    id = Column(Integer, primary_key=True, index=True)
    gesture_id = Column(Integer, ForeignKey("gestures.id", ondelete="CASCADE"))
    sequence_data = Column(Text)  # Stores serialized JSON of 30x21x3 keypoints
    is_augmented = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    gesture = relationship("Gesture", back_populates="training_data")
