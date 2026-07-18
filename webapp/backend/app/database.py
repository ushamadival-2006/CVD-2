from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100))
    email         = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255))
    google_id     = Column(String(255), unique=True, nullable=True)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    predictions   = relationship("Prediction", back_populates="user")

class Prediction(Base):
    __tablename__ = "predictions"
    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_name     = Column(String(100))
    risk_score       = Column(Float)
    risk_level       = Column(String(20))
    confidence       = Column(String(20))
    source           = Column(String(30))
    clinical_data    = Column(Text)   # JSON string
    image_path       = Column(String(255), nullable=True)
    shap_explanation = Column(Text, nullable=True)  # JSON string
    gradcam_path     = Column(String(255), nullable=True)
    recommendations  = Column(Text)   # JSON string
    created_at       = Column(DateTime, default=datetime.utcnow)
    user             = relationship("User", back_populates="predictions")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
