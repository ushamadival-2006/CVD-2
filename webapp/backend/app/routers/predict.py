import json, os, uuid, time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..database import get_db, Prediction, User
from ..auth import get_current_user
from ..schemas import PredictionResponse, PredictionHistoryItem, ExplanationData, RecommendationData
from ..services.clinical_service import predict_clinical
from ..services.retinal_service import predict_retinal
from ..services.agents import run_agentic_pipeline, explain_risk, explain_gradcam
from ..config import settings

router = APIRouter(prefix="/predict", tags=["Predictions"])


def _risk_label(score: float) -> str:
    if score < 30:  return "LOW RISK"
    if score <= 70: return "INTERMEDIARY RISK"
    return "HIGH RISK"

def _confidence(score: float) -> str:
    diff = abs(score - 50)
    if diff >= 30: return "High"
    if diff >= 15: return "Moderate"
    return "Low"


@router.post("/fusion", response_model=PredictionResponse)
async def predict_fusion(
    age:                 float = Form(...),
    gender:              str   = Form(...),
    height_cm:           float = Form(...),
    weight_kg:           float = Form(...),
    systolic_bp:         float = Form(...),
    diastolic_bp:        float = Form(...),
    total_cholesterol:   float = Form(...),
    hdl:                 float = Form(...),
    fasting_blood_sugar: float = Form(...),
    smoking_status:      str   = Form(...),
    diabetes_status:     str   = Form(...),
    physical_activity:   str   = Form(...),
    family_history_cvd:  str   = Form(...),
    patient_name:        Optional[str]    = Form(None),
    # Two eye uploads — either or both can be provided
    left_eye_image:      Optional[UploadFile] = File(None),
    right_eye_image:     Optional[UploadFile] = File(None),
    db:                  Session = Depends(get_db),
    current_user:        User    = Depends(get_current_user),
):
    clinical_data = dict(
        age=age, gender=gender, height_cm=height_cm, weight_kg=weight_kg,
        systolic_bp=systolic_bp, diastolic_bp=diastolic_bp,
        total_cholesterol=total_cholesterol, hdl=hdl,
        fasting_blood_sugar=fasting_blood_sugar, smoking_status=smoking_status,
        diabetes_status=diabetes_status, physical_activity=physical_activity,
        family_history_cvd=family_history_cvd,
    )

    # ── Clinical prediction ───────────────────────────────────────────────────
    clin_result   = predict_clinical(clinical_data)
    clinical_risk = clin_result["risk_score"]
    shap_dict     = clin_result["shap"]

    # ── Retinal prediction (left + right eye, average if both provided) ───────
    retinal_scores   = []
    gradcam_results  = {}   # {"left": b64, "right": b64}
    gradcam_explains = {}   # {"left": text, "right": text}

    for eye_label, upload in [("left",  left_eye_image),
                               ("right", right_eye_image)]:
        if upload and upload.filename:
            img_bytes = await upload.read()
            if len(img_bytes) == 0:
                continue
            result = predict_retinal(img_bytes)
            score  = result.get("risk_score")
            if score is not None:
                retinal_scores.append(score)
                gradcam_results[eye_label] = result.get("gradcam")

    # Average both eye scores if available
    retinal_risk = None
    if retinal_scores:
        retinal_risk = round(sum(retinal_scores) / len(retinal_scores), 2)

    # Combined Grad-CAM: prefer left+right; fall back to whichever is available
    gradcam_b64 = None
    if gradcam_results:
        # Return left eye Grad-CAM as primary; right stored separately
        gradcam_b64 = gradcam_results.get("left") or gradcam_results.get("right")

    # ── Fusion score ──────────────────────────────────────────────────────────
    if retinal_risk is not None:
        fusion_score = round(0.6 * clinical_risk + 0.4 * retinal_risk, 2)
        n_eyes  = len(retinal_scores)
        source  = f"Multimodal Fusion ({n_eyes} eye{'s' if n_eyes > 1 else ''})"
    else:
        fusion_score = clinical_risk
        source       = "Clinical Only"

    risk_level = _risk_label(fusion_score)
    confidence = _confidence(fusion_score)

    # ── LLM risk explanation (SHAP interpreter) ───────────────────────────────
    time.sleep(2)
    risk_explanation = explain_risk(
        risk_score   = fusion_score,
        risk_level   = risk_level,
        clinical     = clinical_data,
        shap_dict    = shap_dict,
        has_retinal  = retinal_risk is not None,
        retinal_risk = retinal_risk,
    )

    # ── Grad-CAM natural language explanations (one per eye) ─────────────────
    for eye_label, eye_score in [
        ("left",  retinal_scores[0] if len(retinal_scores) >= 1 else None),
        ("right", retinal_scores[1] if len(retinal_scores) >= 2 else
                  (retinal_scores[0] if "right" in gradcam_results and len(retinal_scores) == 1 else None)),
    ]:
        if eye_label in gradcam_results and eye_score is not None:
            time.sleep(2)
            gradcam_explains[eye_label] = explain_gradcam(
                retinal_risk = eye_score,
                clinical     = clinical_data,
                fusion_score = fusion_score,
                risk_level   = risk_level,
                eye_label    = f"{eye_label} eye",
            )

    # ── 3-Agent recommendation pipeline ──────────────────────────────────────
    time.sleep(2)
    recs = run_agentic_pipeline(fusion_score, risk_level, clinical_data)

    # ── Save to DB ────────────────────────────────────────────────────────────
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    image_path = None
    for eye_label, upload in [("left", left_eye_image), ("right", right_eye_image)]:
        if upload and upload.filename:
            fname      = f"{uuid.uuid4().hex}_{eye_label}_{upload.filename}"
            image_path = os.path.join(settings.UPLOAD_DIR, fname)

    # Store both gradcam paths in shap_explanation field as extra JSON
    extra = {}
    if gradcam_results.get("right"):
        extra["gradcam_right"] = gradcam_results["right"]
    if gradcam_explains.get("left"):
        extra["gradcam_explain_left"]  = gradcam_explains["left"]
    if gradcam_explains.get("right"):
        extra["gradcam_explain_right"] = gradcam_explains["right"]

    pred_db = Prediction(
        user_id          = current_user.id,
        patient_name     = patient_name or current_user.name,
        risk_score       = fusion_score,
        risk_level       = risk_level,
        confidence       = confidence,
        source           = source,
        clinical_data    = json.dumps(clinical_data),
        image_path       = image_path,
        shap_explanation = json.dumps({**shap_dict, **extra}),
        gradcam_path     = None,
        recommendations  = json.dumps({**recs, "risk_explanation": risk_explanation}),
    )
    db.add(pred_db); db.commit(); db.refresh(pred_db)

    # Build explanation — include both eye Grad-CAMs
    explanation = ExplanationData(
        shap    = shap_dict,
        gradcam = gradcam_b64,
    )
    # Add right eye if available
    if gradcam_results.get("right"):
        explanation.gradcam_right = gradcam_results["right"]  # type: ignore

    return PredictionResponse(
        patient_id       = str(pred_db.id),
        risk_score       = fusion_score,
        risk_level       = risk_level,
        confidence       = confidence,
        source           = source,
        timestamp        = pred_db.created_at,
        risk_explanation = risk_explanation,
        explanation      = explanation,
        recommendations  = RecommendationData(**recs),
    )


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preds = (db.query(Prediction)
             .filter(Prediction.user_id == current_user.id)
             .order_by(Prediction.created_at.desc())
             .all())
    return [PredictionHistoryItem.model_validate(p) for p in preds]


@router.get("/{prediction_id}")
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pred = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == current_user.id
    ).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    raw_shap = json.loads(pred.shap_explanation) if pred.shap_explanation else {}
    gradcam_right = raw_shap.pop("gradcam_right", None)
    recs          = json.loads(pred.recommendations) if pred.recommendations else {}
    risk_exp      = recs.pop("risk_explanation", None)

    return {
        "id":            pred.id,
        "patient_name":  pred.patient_name,
        "risk_score":    pred.risk_score,
        "risk_level":    pred.risk_level,
        "confidence":    pred.confidence,
        "source":        pred.source,
        "created_at":    pred.created_at,
        "clinical_data": json.loads(pred.clinical_data) if pred.clinical_data else {},
        "risk_explanation": risk_exp,
        "explanation":   {"shap": raw_shap, "gradcam": None, "gradcam_right": gradcam_right},
        "recommendations": recs,
    }
