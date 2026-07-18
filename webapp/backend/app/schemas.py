from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

# ── Auth ──────────────────────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    token: str  # Google ID token from frontend

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    class Config:
        from_attributes = True

# ── Clinical Input ─────────────────────────────────────────────────────────────
class ClinicalInput(BaseModel):
    age: float = Field(..., ge=18, le=120, description="Age in years")
    gender: str = Field(..., pattern="^[MF]$")
    height_cm: float = Field(..., ge=100, le=250)
    weight_kg: float = Field(..., ge=30, le=300)
    systolic_bp: float = Field(..., ge=70, le=250)
    diastolic_bp: float = Field(..., ge=40, le=150)
    total_cholesterol: float = Field(..., ge=50, le=500)
    hdl: float = Field(..., ge=10, le=200)
    fasting_blood_sugar: float = Field(..., ge=50, le=600)
    smoking_status: str = Field(..., pattern="^[YN]$")
    diabetes_status: str = Field(..., pattern="^[YN]$")
    physical_activity: str = Field(..., pattern="^(Low|Moderate|High)$")
    family_history_cvd: str = Field(..., pattern="^[YN]$")
    patient_name: Optional[str] = Field(None, max_length=100)

# ── Prediction Response ────────────────────────────────────────────────────────
class ExplanationData(BaseModel):
    shap: Optional[Dict[str, float]] = None
    gradcam: Optional[str] = None              # left eye or single eye base64
    gradcam_right: Optional[str] = None        # right eye base64 (if uploaded)
    gradcam_explanation: Optional[str] = None  # LLM explanation for left/primary eye
    gradcam_explanation_right: Optional[str] = None  # LLM explanation for right eye

class RecommendationData(BaseModel):
    diet: str
    exercise: str
    medical_guidance: str
    powered_by: str = "Rule-Based Engine"

class PredictionResponse(BaseModel):
    patient_id: str
    risk_score: float
    risk_level: str
    confidence: str
    source: str
    timestamp: datetime
    risk_explanation: Optional[str] = None   # LLM explanation of SHAP/Grad-CAM
    explanation: ExplanationData
    recommendations: RecommendationData

class PredictionHistoryItem(BaseModel):
    id: int
    patient_name: Optional[str]
    risk_score: float
    risk_level: str
    confidence: str
    source: str
    created_at: datetime
    class Config:
        from_attributes = True
