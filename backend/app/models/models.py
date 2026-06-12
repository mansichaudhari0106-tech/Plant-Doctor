from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    plants = relationship("Plant", back_populates="owner", cascade="all, delete-orphan")


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, default="unknown")  # healthy / recovering / critical / unknown
    planted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="plants")
    photos = relationship("Photo", back_populates="plant", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="plant", cascade="all, delete-orphan")
    care_plans = relationship("CarePlan", back_populates="plant", cascade="all, delete-orphan")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    filepath = Column(String, nullable=False)
    taken_at = Column(DateTime, default=datetime.utcnow)
    note = Column(Text, nullable=True)

    plant = relationship("Plant", back_populates="photos")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=True)
    symptom_category = Column(String, nullable=True)  # water/light/pest/nutrient/disease
    diagnosis_text = Column(Text, nullable=True)
    species_guess = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    plant = relationship("Plant", back_populates="diagnoses")


class CarePlan(Base):
    __tablename__ = "care_plans"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=True)
    plan_text = Column(Text, nullable=False)
    expected_recovery = Column(String, nullable=True)
    checklist_json = Column(Text, nullable=True)  # JSON-encoded list of {item, done}
    created_at = Column(DateTime, default=datetime.utcnow)

    plant = relationship("Plant", back_populates="care_plans")


class ConversationState(Base):
    """Stores LangGraph thread state / pending clarifying questions per plant session."""
    __tablename__ = "conversation_states"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, unique=True)
    thread_id = Column(String, nullable=False)
    pending_questions_json = Column(Text, nullable=True)  # JSON list of questions
    answers_json = Column(Text, nullable=True)  # JSON list of answers
    awaiting_input = Column(Boolean, default=False)
    state_json = Column(Text, nullable=True)  # serialized intermediate state
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
