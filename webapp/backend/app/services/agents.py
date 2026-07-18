"""
Agentic AI Recommendation Engine
==================================
3-agent sequential pipeline powered by Google Gemini (google-genai SDK).

Agent 1: Diet Recommendation Agent
Agent 2: Exercise Recommendation Agent
Agent 3: Health Guidance Agent

Falls back to rule-based recommendations if Gemini API is unavailable.
"""

import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)

# ── Gemini client (new google-genai SDK) ──────────────────────────────────────
_gemini_client = None

def _get_gemini():
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        logger.info("GEMINI_API_KEY not set — using rule-based fallback.")
        return None
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini client initialised successfully.")
        return _gemini_client
    except Exception as e:
        logger.warning(f"Gemini setup failed: {e}")
        return None


def _call_gemini(prompt: str) -> Optional[str]:
    """Call Gemini API. Returns text or None on failure."""
    client = _get_gemini()
    if client is None:
        return None
    try:
        from google import genai
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        return response.text.strip() if response.text else None
    except Exception as e:
        logger.warning(f"Gemini API call failed: {e}")
        return None


# ── Patient context builder ────────────────────────────────────────────────────
def _build_patient_summary(risk_score: float, risk_level: str, clinical: dict) -> str:
    height_m  = clinical.get('height_cm', 170) / 100
    weight    = clinical.get('weight_kg', 70)
    bmi       = round(weight / (height_m ** 2), 1)
    age       = clinical.get('age', 50)
    gender    = 'Male' if clinical.get('gender', 'M') == 'M' else 'Female'
    systolic  = clinical.get('systolic_bp', 120)
    diastolic = clinical.get('diastolic_bp', 80)
    chol      = clinical.get('total_cholesterol', 200)
    hdl       = clinical.get('hdl', 50)
    fbs       = clinical.get('fasting_blood_sugar', 100)
    smoking   = 'Yes' if clinical.get('smoking_status', 'N') == 'Y' else 'No'
    diabetes  = 'Yes' if clinical.get('diabetes_status', 'N') == 'Y' else 'No'
    family    = 'Yes' if clinical.get('family_history_cvd', 'N') == 'Y' else 'No'
    activity  = clinical.get('physical_activity', 'Moderate')

    return f"""Patient Profile:
- Age: {age} years, Gender: {gender}
- BMI: {bmi} (Weight: {weight}kg, Height: {clinical.get('height_cm', 170)}cm)
- Blood Pressure: {systolic}/{diastolic} mmHg
- Total Cholesterol: {chol} mg/dL, HDL: {hdl} mg/dL
- Fasting Blood Sugar: {fbs} mg/dL
- Smoking: {smoking}, Diabetes: {diabetes}
- Family History of CVD: {family}
- Physical Activity Level: {activity}
- CVD Risk Score: {risk_score:.1f}% — {risk_level}"""


# ── AGENT 1: Diet Recommendation Agent ────────────────────────────────────────
def _agent1_diet(patient_summary: str, risk_score: float, clinical: dict) -> str:
    prompt = f"""You are Agent 1: Diet Recommendation Agent for a cardiovascular disease risk assessment system.
You are a clinical nutritionist specialising in heart health and preventive cardiology.

{patient_summary}

Based on this patient's specific health profile, generate a personalised, evidence-based dietary recommendation.
Include:
1. Specific foods to eat and avoid (tailored to their cholesterol, blood sugar, and BMI)
2. A brief sample meal plan for one day
3. Specific portion sizes or quantities where relevant
4. Any nutritional targets (e.g. sodium limit, fibre goal)

Important:
- Be specific to THIS patient's numbers (reference actual values)
- Keep response under 200 words
- Warm, supportive, medical professional tone
- Plain paragraphs only — no markdown headers or bullet symbols"""

    result = _call_gemini(prompt)
    if result:
        logger.info("Agent 1 (Diet): Gemini response received.")
        return result
    from .recommendation_service import get_recommendations
    return get_recommendations(risk_score, clinical)['diet']


# ── AGENT 2: Exercise Recommendation Agent ────────────────────────────────────
def _agent2_exercise(patient_summary: str, risk_score: float, clinical: dict,
                     diet_recommendation: str) -> str:
    prompt = f"""You are Agent 2: Exercise Recommendation Agent in a cardiovascular disease risk assessment pipeline.
You are a certified cardiac rehabilitation specialist.

{patient_summary}

The Diet Agent (Agent 1) has already provided this recommendation:
"{diet_recommendation[:400]}"

Now generate a personalised exercise plan that complements the diet recommendation above.
Include:
1. Specific exercise types suitable for this patient's age, BMI, and risk level
2. A weekly schedule (e.g. Week 1: ..., Week 2: ...)
3. Duration, intensity, and frequency
4. Warning signs to stop exercising and seek medical attention
5. Progress milestones for the first month

Important:
- Be specific to this patient's age ({clinical.get('age', 50)}) and risk level
- If HIGH risk, be conservative and emphasise medical clearance first
- Reference their current activity level ({clinical.get('physical_activity', 'Moderate')})
- Keep response under 200 words
- Warm, motivating, medical professional tone
- Plain paragraphs only — no markdown headers or bullet symbols"""

    result = _call_gemini(prompt)
    if result:
        logger.info("Agent 2 (Exercise): Gemini response received.")
        return result
    from .recommendation_service import get_recommendations
    return get_recommendations(risk_score, clinical)['exercise']


# ── AGENT 3: Health Guidance Agent ────────────────────────────────────────────
def _agent3_health_guidance(patient_summary: str, risk_score: float, clinical: dict,
                             diet_rec: str, exercise_rec: str) -> str:
    prompt = f"""You are Agent 3: Health Guidance Agent — the final agent in a cardiovascular risk assessment pipeline.
You are a senior cardiologist providing holistic medical guidance.

{patient_summary}

Previous agents have recommended:
- Diet Agent: "{diet_rec[:250]}"
- Exercise Agent: "{exercise_rec[:250]}"

Now provide comprehensive medical guidance. Include:
1. Urgency level — should this patient see a doctor today, this week, or at next annual checkup?
2. Specific medical tests recommended (name them explicitly)
3. Medications to discuss with their doctor if applicable
4. Specific risk factors that need immediate attention
5. Lifestyle changes beyond diet and exercise
6. Follow-up timeline

Important:
- Be direct about urgency if risk is HIGH
- Reference specific values (smoking: {clinical.get('smoking_status','N')}, family history: {clinical.get('family_history_cvd','N')})
- Always recommend consulting a qualified physician for final decisions
- Keep response under 200 words
- Authoritative but compassionate medical tone
- Plain paragraphs only — no markdown headers or bullet symbols"""

    result = _call_gemini(prompt)
    if result:
        logger.info("Agent 3 (Health Guidance): Gemini response received.")
        return result
    from .recommendation_service import get_recommendations
    return get_recommendations(risk_score, clinical)['medical_guidance']


# ── Orchestrator: Sequential Pipeline ─────────────────────────────────────────
def run_agentic_pipeline(risk_score: float, risk_level: str, clinical: dict) -> dict:
    """
    Sequential 3-agent pipeline:
      Agent 1 (Diet) → Agent 2 (Exercise, uses Agent 1 output)
                     → Agent 3 (Health Guidance, uses Agent 1 + 2 outputs)

    Falls back to rule-based engine if Gemini is unavailable.
    Returns: dict with diet, exercise, medical_guidance, powered_by
    """
    using_llm = _get_gemini() is not None
    logger.info(f"Starting pipeline | risk={risk_score:.1f}% | engine={'Gemini' if using_llm else 'RuleBased'}")

    patient_summary = _build_patient_summary(risk_score, risk_level, clinical)

    logger.info("Running Agent 1: Diet...")
    diet = _agent1_diet(patient_summary, risk_score, clinical)

    import time; time.sleep(4)   # respect free-tier rate limit (15 RPM)
    logger.info("Running Agent 2: Exercise...")
    exercise = _agent2_exercise(patient_summary, risk_score, clinical, diet)

    time.sleep(4)
    logger.info("Running Agent 3: Health Guidance...")
    health = _agent3_health_guidance(patient_summary, risk_score, clinical, diet, exercise)

    powered_by = "Gemini AI — 3 Agents (Diet → Exercise → Health)" if using_llm else "Rule-Based Engine"
    logger.info(f"Pipeline complete. powered_by={powered_by}")

    return {
        "diet":             diet,
        "exercise":         exercise,
        "medical_guidance": health,
        "powered_by":       powered_by,
    }


# ── Risk Explanation Agent (SHAP + Grad-CAM interpreter) ──────────────────────
def explain_risk(
    risk_score: float,
    risk_level: str,
    clinical: dict,
    shap_dict: dict,
    has_retinal: bool = False,
    retinal_risk: float = None,
) -> str:
    """
    Reads SHAP feature importances and generates a natural language explanation
    of WHY the patient has their specific risk score.

    This is called AFTER SHAP and Grad-CAM are computed and explains the
    model's reasoning in plain, patient-friendly language.
    """
    # Build SHAP top-factors summary
    # Sort by absolute SHAP value, take top 6
    top_factors = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:6]

    # Map encoded feature names back to human-readable labels
    name_map = {
        'Smoking Status_Encoded':        'Smoking status',
        'Family History of CVD_Encoded': 'Family history of CVD',
        'Diabetes Status_Encoded':       'Diabetes status',
        'Age_Elderly':                   'Elderly age group',
        'Age_Senior':                    'Senior age group',
        'Age_Middle':                    'Middle age group',
        'Age_Adult':                     'Adult age group',
        'Age_Young':                     'Young age group',
        'BMI_Obese':                     'Obesity (BMI ≥ 30)',
        'BMI_Overweight':                'Overweight (BMI 25-30)',
        'BMI_Normal':                    'Normal BMI',
        'BMI_Underweight':               'Underweight BMI',
        'Cholesterol_HDL_Ratio':         'Cholesterol-to-HDL ratio',
        'Metabolic_Score':               'Metabolic risk score',
        'Obesity_Risk':                  'Obesity risk',
        'Hypertension_Risk':             'Hypertension risk',
        'Blood_Pressure_Encoded':        'Blood pressure category',
        'Physical_Activity_Encoded':     'Physical activity level',
        'CVD Risk Score':                'Composite CVD risk score',
        'Systolic BP':                   'Systolic blood pressure',
        'Diastolic BP':                  'Diastolic blood pressure',
        'Total Cholesterol (mg/dL)':     'Total cholesterol',
        'HDL (mg/dL)':                   'HDL (good cholesterol)',
        'Fasting Blood Sugar (mg/dL)':   'Fasting blood sugar',
        'Age':                           'Age',
        'BMI':                           'Body Mass Index (BMI)',
        'Weight (kg)':                   'Body weight',
        'Pulse Pressure':                'Pulse pressure',
    }

    factors_text = "\n".join([
        f"  - {name_map.get(name, name)}: SHAP = {val:+.4f} ({'increases' if val > 0 else 'decreases'} risk)"
        for name, val in top_factors
    ])

    # Build retinal context if available
    retinal_context = ""
    if has_retinal and retinal_risk is not None:
        retinal_context = f"""
Retinal Image Analysis:
  - Retinal CIMT risk score: {retinal_risk:.1f}%
  - The retinal model identified vascular changes consistent with {'elevated' if retinal_risk > 50 else 'moderate'} cardiovascular risk.
  - Final score is a fusion: 0.6 × clinical ({clinical.get('age', '?')}yr patient) + 0.4 × retinal."""

    # Build clinical context
    height_m = clinical.get('height_cm', 170) / 100
    bmi = round(clinical.get('weight_kg', 70) / (height_m ** 2), 1)

    prompt = f"""You are a medical AI assistant explaining cardiovascular disease risk to a patient in plain, empathetic language.

Patient Profile:
- Age: {clinical.get('age', '?')} years, Gender: {'Male' if clinical.get('gender','M')=='M' else 'Female'}
- BMI: {bmi}, Blood Pressure: {clinical.get('systolic_bp','?')}/{clinical.get('diastolic_bp','?')} mmHg
- Total Cholesterol: {clinical.get('total_cholesterol','?')} mg/dL, HDL: {clinical.get('hdl','?')} mg/dL
- Smoking: {'Yes' if clinical.get('smoking_status','N')=='Y' else 'No'}
- Diabetes: {'Yes' if clinical.get('diabetes_status','N')=='Y' else 'No'}
- Family History of CVD: {'Yes' if clinical.get('family_history_cvd','N')=='Y' else 'No'}

AI Model Result:
- CVD Risk Score: {risk_score:.1f}% — {risk_level}

Top factors identified by the AI model (SHAP analysis):
{factors_text}
{retinal_context}

Task:
Write a clear, warm, and empathetic explanation (3-4 short paragraphs) that:
1. States the overall risk level and what it means in plain language
2. Explains the TOP 3 most important factors driving this risk score — use the patient's actual numbers
3. Explains any protective factors (negative SHAP = reduces risk) if present
4. Ends with a hopeful, motivating message about what they can do

Rules:
- Write in second person ("Your blood pressure of 145/92...")
- Reference actual patient values, not generic statements
- Keep total response under 200 words
- Warm, non-alarming tone — informative but not scary
- Plain paragraphs only, no bullet points or headers"""

    result = _call_gemini(prompt)
    if result:
        logger.info("Risk explanation generated by Gemini.")
        return result

    # Fallback: rule-based explanation
    top3 = top_factors[:3]
    explanation = (
        f"Your CVD risk score is {risk_score:.1f}%, which places you in the {risk_level} category. "
        f"The AI model identified the following as your most significant risk factors: "
        + ", ".join([name_map.get(n, n) for n, v in top3 if v > 0])
        + ". "
    )
    if any(v < 0 for _, v in top3):
        protective = [name_map.get(n, n) for n, v in top3 if v < 0]
        if protective:
            explanation += f"On the positive side, {', '.join(protective)} are working in your favour. "
    explanation += "With the right lifestyle changes and medical guidance, you can significantly reduce your risk."
    return explanation


# ── Grad-CAM Natural Language Explanation Agent ───────────────────────────────
def explain_gradcam(
    retinal_risk: float,
    clinical: dict,
    fusion_score: float,
    risk_level: str,
    eye_label: str = "retinal",
) -> str:
    """
    Generates a natural language explanation of what the Grad-CAM heatmap
    means clinically — why the retinal image contributed to the risk score.

    Parameters:
        retinal_risk:  risk score from the retinal model (0-100)
        clinical:      patient clinical data dict
        fusion_score:  final fused risk score
        risk_level:    e.g. "HIGH RISK"
        eye_label:     "left eye", "right eye", or "retinal"
    """
    # Derive clinical context
    height_m    = clinical.get('height_cm', 170) / 100
    bmi         = round(clinical.get('weight_kg', 70) / (height_m ** 2), 1)
    age         = clinical.get('age', 50)
    systolic    = clinical.get('systolic_bp', 120)
    diastolic   = clinical.get('diastolic_bp', 80)
    diabetes    = 'Yes' if clinical.get('diabetes_status', 'N') == 'Y' else 'No'
    smoking     = 'Yes' if clinical.get('smoking_status', 'N') == 'Y' else 'No'

    # Interpret retinal risk severity
    if retinal_risk >= 70:
        severity        = "significant"
        vessel_desc     = "markedly thickened and irregular"
        cimt_estimate   = "≥ 1.1 mm (thickened)"
        progression     = "advanced vascular changes"
    elif retinal_risk >= 50:
        severity        = "moderate"
        vessel_desc     = "mildly thickened with visible irregularities"
        cimt_estimate   = "0.9–1.0 mm (borderline)"
        progression     = "early-to-moderate vascular changes"
    elif retinal_risk >= 30:
        severity        = "mild"
        vessel_desc     = "slightly thickened at some arterial crossings"
        cimt_estimate   = "0.8–0.9 mm (near normal)"
        progression     = "early vascular changes"
    else:
        severity        = "minimal"
        vessel_desc     = "appear normal with good vascular tone"
        cimt_estimate   = "< 0.8 mm (normal)"
        progression     = "no significant vascular changes"

    # Calculate retinal contribution to fusion
    retinal_contribution = round(0.4 * retinal_risk, 1)
    clinical_risk_est    = round((fusion_score - 0.4 * retinal_risk) / 0.6, 1)

    prompt = f"""You are a retinal imaging specialist explaining a Grad-CAM heatmap result to a patient.

Patient Profile:
- Age: {age} years, BMI: {bmi}
- Blood Pressure: {systolic}/{diastolic} mmHg
- Diabetes: {diabetes}, Smoking: {smoking}

Retinal Analysis ({eye_label}):
- Retinal CIMT Risk Score: {retinal_risk:.1f}%
- Severity: {severity}
- Retinal vessel appearance: {vessel_desc}
- Estimated CIMT (Carotid Intima-Media Thickness equivalent): {cimt_estimate}
- Vascular finding: {progression}

Risk Score Breakdown:
- Clinical model contributed: {clinical_risk_est:.1f}% × 60% = {round(0.6*clinical_risk_est,1)}%
- Retinal model contributed: {retinal_risk:.1f}% × 40% = {retinal_contribution}%
- Final fused score: {fusion_score:.1f}% — {risk_level}

Task:
Write a clear, warm, empathetic explanation (2-3 short paragraphs) that:
1. Explains what the Grad-CAM heatmap shows — which regions of the retinal image the AI focused on and why
2. Explains what the retinal vessel findings mean clinically — connect vessel thickness/changes to cardiovascular risk
3. Explains how much the retinal image contributed to the final risk score using the actual numbers above

Rules:
- Write in second person ("Your retinal scan shows...")
- Use plain language — no medical jargon without explanation
- Reference the actual retinal risk score ({retinal_risk:.1f}%) and its contribution ({retinal_contribution}%)
- Explain what CIMT means simply: "The thickness of the vessel walls in your eye mirrors the health of vessels in your heart and arteries"
- Keep total response under 180 words
- Warm, non-alarming but honest tone
- Plain paragraphs only, no bullet points or headers"""

    result = _call_gemini(prompt)
    if result:
        logger.info(f"Grad-CAM explanation generated by Gemini ({eye_label}).")
        return result

    # Fallback: rule-based explanation
    fallback = (
        f"Your {eye_label} scan shows {vessel_desc}. "
        f"The AI model identified these retinal vessel patterns as consistent with {progression}. "
        f"The retinal vessels in your eye act as a window into the health of your cardiovascular system — "
        f"thicker or more irregular vessels here often mirror similar changes in your heart and arteries. "
        f"Your retinal CIMT score is {retinal_risk:.1f}%, which contributed {retinal_contribution}% "
        f"(40% weighting) to your final risk score of {fusion_score:.1f}%."
    )
    return fallback
