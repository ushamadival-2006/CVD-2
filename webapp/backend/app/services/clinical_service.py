import numpy as np
import pandas as pd
import joblib
import shap
import base64
import io
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ..config import settings

# Lazy-load model and scaler once
_model = None
_scaler = None
_explainer = None

FEATURE_COLS = [
    'Age', 'Weight (kg)', 'Height (m)', 'BMI',
    'Abdominal Circumference (cm)', 'Total Cholesterol (mg/dL)',
    'HDL (mg/dL)', 'Fasting Blood Sugar (mg/dL)',
    'Waist-to-Height Ratio', 'Systolic BP', 'Diastolic BP',
    'CVD Risk Score', 'Pulse Pressure', 'Cholesterol_HDL_Ratio',
    'Obesity_Risk', 'Hypertension_Risk', 'Metabolic_Score',
    'Sex_Encoded', 'Smoking Status_Encoded', 'Diabetes Status_Encoded',
    'Family History of CVD_Encoded', 'Physical_Activity_Encoded',
    'Blood_Pressure_Encoded',
    'BMI_Normal', 'BMI_Obese', 'BMI_Overweight', 'BMI_Underweight',
    'Age_Adult', 'Age_Elderly', 'Age_Middle', 'Age_Senior', 'Age_Young'
]

SCALE_COLS = [
    'Age', 'Weight (kg)', 'Height (m)', 'BMI',
    'Abdominal Circumference (cm)', 'Total Cholesterol (mg/dL)',
    'HDL (mg/dL)', 'Fasting Blood Sugar (mg/dL)',
    'Waist-to-Height Ratio', 'Systolic BP', 'Diastolic BP',
    'CVD Risk Score', 'Pulse Pressure', 'Cholesterol_HDL_Ratio',
    'Metabolic_Score', 'Physical_Activity_Encoded'
]

def _load_models():
    global _model, _scaler, _explainer
    if _model is None:
        model_path  = os.path.abspath(settings.MODEL_PATH)
        scaler_path = os.path.abspath(settings.SCALER_PATH)
        _model  = joblib.load(model_path)
        _scaler = joblib.load(scaler_path)
        _explainer = shap.TreeExplainer(_model)

def _build_features(data: dict) -> pd.DataFrame:
    age       = data['age']
    weight    = data['weight_kg']
    height_m  = data['height_cm'] / 100.0
    bmi       = weight / (height_m ** 2)
    systolic  = data['systolic_bp']
    diastolic = data['diastolic_bp']
    chol      = data['total_cholesterol']
    hdl       = data['hdl']
    fbs       = data['fasting_blood_sugar']

    abdominal     = bmi * 0.85 * height_m * 100  # estimate
    whr           = abdominal / (height_m * 100)
    pulse         = systolic - diastolic
    chol_hdl      = chol / hdl if hdl > 0 else 0
    obesity       = 1 if bmi >= 30 else 0
    hypert        = 1 if (systolic >= 140 or diastolic >= 90) else 0
    smoking_enc   = 1 if data['smoking_status'] == 'Y' else 0
    diabetes_enc  = 1 if data['diabetes_status'] == 'Y' else 0
    family_enc    = 1 if data['family_history_cvd'] == 'Y' else 0
    sex_enc       = 0 if data['gender'] == 'F' else 1
    activity_enc  = {'Low': 0, 'Moderate': 1, 'High': 2}.get(data['physical_activity'], 1)
    bp_enc        = (0 if systolic < 120 and diastolic < 80
                     else 1 if systolic < 130 and diastolic < 80
                     else 2 if systolic < 140 or diastolic < 90
                     else 3)
    metabolic     = (obesity + hypert
                     + (1 if chol >= 240 else 0)
                     + (1 if fbs >= 126 else 0)
                     + smoking_enc)
    cvd_score     = float(np.clip(
        10.0 + 0.05*age + 0.01*(systolic-90) + 0.005*(chol-100)
        - 0.02*(hdl-30) + (1.0 if smoking_enc else 0)
        + (0.8 if diabetes_enc else 0) + (0.5 if family_enc else 0)
        + (0.3 if obesity else 0), 10.5, 24.2))

    bmi_cat = ('Underweight' if bmi < 18.5 else 'Normal' if bmi < 25
               else 'Overweight' if bmi < 30 else 'Obese')
    age_grp = ('Young' if age < 35 else 'Adult' if age < 50
               else 'Middle' if age < 60 else 'Senior' if age < 70 else 'Elderly')

    row = {
        'Age': age, 'Weight (kg)': weight, 'Height (m)': height_m,
        'BMI': bmi, 'Abdominal Circumference (cm)': abdominal,
        'Total Cholesterol (mg/dL)': chol, 'HDL (mg/dL)': hdl,
        'Fasting Blood Sugar (mg/dL)': fbs, 'Waist-to-Height Ratio': whr,
        'Systolic BP': systolic, 'Diastolic BP': diastolic,
        'CVD Risk Score': cvd_score, 'Pulse Pressure': pulse,
        'Cholesterol_HDL_Ratio': chol_hdl, 'Obesity_Risk': obesity,
        'Hypertension_Risk': hypert, 'Metabolic_Score': metabolic,
        'Sex_Encoded': sex_enc, 'Smoking Status_Encoded': smoking_enc,
        'Diabetes Status_Encoded': diabetes_enc,
        'Family History of CVD_Encoded': family_enc,
        'Physical_Activity_Encoded': activity_enc,
        'Blood_Pressure_Encoded': bp_enc,
        'BMI_Normal':      1 if bmi_cat == 'Normal' else 0,
        'BMI_Obese':       1 if bmi_cat == 'Obese' else 0,
        'BMI_Overweight':  1 if bmi_cat == 'Overweight' else 0,
        'BMI_Underweight': 1 if bmi_cat == 'Underweight' else 0,
        'Age_Adult':   1 if age_grp == 'Adult' else 0,
        'Age_Elderly': 1 if age_grp == 'Elderly' else 0,
        'Age_Middle':  1 if age_grp == 'Middle' else 0,
        'Age_Senior':  1 if age_grp == 'Senior' else 0,
        'Age_Young':   1 if age_grp == 'Young' else 0,
    }
    df = pd.DataFrame([row])[FEATURE_COLS]
    scale_present = [c for c in SCALE_COLS if c in df.columns]
    df[scale_present] = _scaler.transform(df[scale_present])
    return df

def _shap_bar_base64(shap_values: np.ndarray, feature_names: list) -> str:
    """Generate SHAP bar chart and return as base64 PNG."""
    importances = dict(zip(feature_names, shap_values.tolist()))
    # Top 10 by absolute value
    top = sorted(importances.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    names  = [t[0] for t in reversed(top)]
    values = [t[1] for t in reversed(top)]
    colors = ['#e74c3c' if v > 0 else '#3498db' for v in values]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(names, values, color=colors)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel('SHAP Value (impact on prediction)')
    ax.set_title('Feature Importance (SHAP)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def predict_clinical(data: dict) -> dict:
    """Run clinical prediction. Returns risk_score (0-100), shap dict, shap_chart_b64."""
    _load_models()
    df = _build_features(data)
    proba       = float(_model.predict_proba(df)[0][1])
    risk_pct    = proba * 100

    # SHAP
    shap_vals   = _explainer.shap_values(df)
    if isinstance(shap_vals, list):
        shap_arr = shap_vals[1][0]
    else:
        shap_arr = shap_vals[0]
    shap_dict   = {name: round(float(val), 4)
                   for name, val in zip(FEATURE_COLS, shap_arr)}
    shap_chart  = _shap_bar_base64(shap_arr, FEATURE_COLS)

    return {
        "risk_score":  round(risk_pct, 2),
        "shap":        shap_dict,
        "shap_chart":  shap_chart,   # base64 PNG
    }
