from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import create_tables
from app.routers import auth, predict
from app.config import settings

app = FastAPI(
    title="CVD Risk Prediction API",
    description="Cardiovascular Disease Risk Prediction using Clinical Data and Retinal Images",
    version="1.0.0",
)

# CORS — allow React dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images as static files
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(predict.router)

@app.on_event("startup")
def on_startup():
    create_tables()
    print("✅ Database tables created")
    print("✅ CVD Risk Prediction API started")

@app.get("/health", tags=["Health"])
def health_check():
    from app.services.agents import _get_gemini
    gemini_active = _get_gemini() is not None
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "CVD Risk Prediction API",
        "llm": "Gemini AI" if gemini_active else "Rule-Based (set GEMINI_API_KEY to enable AI)",
        "agents": 3 if gemini_active else 0,
    }

@app.get("/", tags=["Root"])
def root():
    return {"message": "CVD Risk Prediction API", "docs": "/docs", "health": "/health"}
