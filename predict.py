"""
CVD Risk Prediction - Patient Input Tool
========================================
Enter patient details and get CVD risk score + label.

Label Logic:
  HIGH chance > INTERMEDIARY chance -> HIGH RISK
  INTERMEDIARY chance > 60%          -> LOW RISK
  Otherwise                          -> INTERMEDIARY RISK
"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# LOAD MODEL AND SCALER
# ============================================================
model  = joblib.load('data/processed/best_model.pkl')
scaler = joblib.load('data/processed/scaler.pkl')

# Feature columns (must match training order exactly)
feature_cols = [
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

scale_cols = [
    'Age', 'Weight (kg)', 'Height (m)', 'BMI',
    'Abdominal Circumference (cm)', 'Total Cholesterol (mg/dL)',
    'HDL (mg/dL)', 'Fasting Blood Sugar (mg/dL)',
    'Waist-to-Height Ratio', 'Systolic BP', 'Diastolic BP',
    'CVD Risk Score', 'Pulse Pressure', 'Cholesterol_HDL_Ratio',
    'Metabolic_Score', 'Physical_Activity_Encoded'
]


def get_bmi_category(bmi):
    if bmi < 18.5:   return 'Underweight'
    elif bmi < 25:   return 'Normal'
    elif bmi < 30:   return 'Overweight'
    else:            return 'Obese'


def get_age_group(age):
    if age < 35:     return 'Young'
    elif age < 50:   return 'Adult'
    elif age < 60:   return 'Middle'
    elif age < 70:   return 'Senior'
    else:            return 'Elderly'


def get_bp_category(systolic, diastolic):
    if systolic < 120 and diastolic < 80:      return 0  # Normal
    elif systolic < 130 and diastolic < 80:    return 1  # Elevated
    elif systolic < 140 or diastolic < 90:     return 2  # Stage 1
    else:                                      return 3  # Stage 2


def predict_risk(patient: dict) -> dict:
    """
    Takes patient dictionary and returns risk score + label.

    Required keys:
        age, weight_kg, height_m, bmi, abdominal_cm,
        total_cholesterol, hdl, fasting_blood_sugar,
        systolic_bp, diastolic_bp,
        sex (M/F), smoking (Y/N), diabetes (Y/N),
        family_history (Y/N), physical_activity (Low/Moderate/High)
    """
    age         = patient['age']
    weight      = patient['weight_kg']
    height_m    = patient['height_m']
    bmi         = patient['bmi']
    abdominal   = patient['abdominal_cm']
    total_chol  = patient['total_cholesterol']
    hdl         = patient['hdl']
    fbs         = patient['fasting_blood_sugar']
    systolic    = patient['systolic_bp']
    diastolic   = patient['diastolic_bp']

    # Derived features
    waist_height_ratio  = abdominal / (height_m * 100)
    pulse_pressure      = systolic - diastolic
    chol_hdl_ratio      = total_chol / hdl if hdl > 0 else 0
    obesity_risk        = 1 if bmi >= 30 else 0
    hypertension_risk   = 1 if (systolic >= 140 or diastolic >= 90) else 0
    smoking_enc         = 1 if patient['smoking'].upper() == 'Y' else 0
    diabetes_enc        = 1 if patient['diabetes'].upper() == 'Y' else 0
    family_enc          = 1 if patient['family_history'].upper() == 'Y' else 0
    sex_enc             = 0 if patient['sex'].upper() == 'F' else 1
    activity_map        = {'Low': 0, 'Moderate': 1, 'High': 2}
    activity_enc        = activity_map.get(patient['physical_activity'], 1)
    bp_enc              = get_bp_category(systolic, diastolic)

    metabolic_score = (
        obesity_risk + hypertension_risk +
        (1 if total_chol >= 240 else 0) +
        (1 if fbs >= 126 else 0) +
        smoking_enc
    )

    # CVD Risk Score (approximated to match dataset range 10.5-24.2)
    cvd_risk_score = (
        10.0 +
        0.05 * age +
        0.01 * (systolic - 90) +
        0.005 * (total_chol - 100) -
        0.02 * (hdl - 30) +
        (1.0 if smoking_enc else 0) +
        (0.8 if diabetes_enc else 0) +
        (0.5 if family_enc else 0) +
        (0.3 if obesity_risk else 0)
    )
    cvd_risk_score = float(np.clip(cvd_risk_score, 10.5, 24.2))

    # BMI and Age one-hot
    bmi_cat  = get_bmi_category(bmi)
    age_grp  = get_age_group(age)

    row = {
        'Age': age, 'Weight (kg)': weight, 'Height (m)': height_m,
        'BMI': bmi, 'Abdominal Circumference (cm)': abdominal,
        'Total Cholesterol (mg/dL)': total_chol, 'HDL (mg/dL)': hdl,
        'Fasting Blood Sugar (mg/dL)': fbs,
        'Waist-to-Height Ratio': waist_height_ratio,
        'Systolic BP': systolic, 'Diastolic BP': diastolic,
        'CVD Risk Score': cvd_risk_score,
        'Sex_Encoded': sex_enc,
        'Smoking Status_Encoded': smoking_enc,
        'Diabetes Status_Encoded': diabetes_enc,
        'Family History of CVD_Encoded': family_enc,
        'Physical_Activity_Encoded': activity_enc,
        'Blood_Pressure_Encoded': bp_enc,
        'Pulse Pressure': pulse_pressure,
        'Cholesterol_HDL_Ratio': chol_hdl_ratio,
        'Obesity_Risk': obesity_risk,
        'Hypertension_Risk': hypertension_risk,
        'Metabolic_Score': metabolic_score,
        'BMI_Normal':      1 if bmi_cat == 'Normal'      else 0,
        'BMI_Obese':       1 if bmi_cat == 'Obese'       else 0,
        'BMI_Overweight':  1 if bmi_cat == 'Overweight'  else 0,
        'BMI_Underweight': 1 if bmi_cat == 'Underweight' else 0,
        'Age_Adult':       1 if age_grp == 'Adult'       else 0,
        'Age_Elderly':     1 if age_grp == 'Elderly'     else 0,
        'Age_Middle':      1 if age_grp == 'Middle'      else 0,
        'Age_Senior':      1 if age_grp == 'Senior'      else 0,
        'Age_Young':       1 if age_grp == 'Young'       else 0,
    }

    df_input = pd.DataFrame([row])[feature_cols]

    # Scale numerical features
    df_scaled = df_input.copy()
    df_scaled[scale_cols] = scaler.transform(df_input[scale_cols])

    # Predict
    proba = model.predict_proba(df_scaled)[0]
    high_chance = proba[1] * 100
    intermediary_chance = proba[0] * 100

    # ============================================================
    # CORRECT LABELING LOGIC
    # ============================================================
    if high_chance > intermediary_chance:
        label = 'HIGH RISK'
    elif intermediary_chance > 60:
        # Very high confidence in INTERMEDIARY = LOW risk
        label = 'LOW RISK'
    else:
        # INTERMEDIARY chance between 40-60% (gray zone)
        label = 'INTERMEDIARY RISK'

    return {
        'risk_score_pct':         round(high_chance, 1),
        'label':                  label,
        'intermediary_prob_pct':  round(intermediary_chance, 1),
        'high_prob_pct':          round(high_chance, 1),
    }


def print_result(patient_name: str, result: dict):
    print(f"\n{'='*50}")
    print(f"  Patient: {patient_name}")
    print(f"{'='*50}")
    print(f"  CVD Risk Score:       {result['risk_score_pct']}%")
    print(f"  Risk Label:           {result['label']}")
    print(f"  INTERMEDIARY chance:  {result['intermediary_prob_pct']}%")
    print(f"  HIGH chance:          {result['high_prob_pct']}%")
    print(f"{'='*50}")


# ============================================================
# TEST PATIENTS - HIGH, INTERMEDIARY, LOW
# ============================================================
if __name__ == '__main__':

    print("\n" + "="*50)
    print("  CVD RISK PREDICTION - DEMO")
    print("  Label Logic:")
    print("    HIGH chance > INTERMEDIARY chance -> HIGH RISK")
    print("    INTERMEDIARY chance > 60%          -> LOW RISK")
    print("    Otherwise                          -> INTERMEDIARY RISK")
    print("="*50)

    # ============================================================
    # PATIENT 1: HIGH RISK
    # HIGH chance > INTERMEDIARY chance
    # ============================================================
    p1 = predict_risk({
        'age': 62,
        'weight_kg': 95,
        'height_m': 1.70,
        'bmi': 32.9,
        'abdominal_cm': 105,
        'total_cholesterol': 265,
        'hdl': 35,
        'fasting_blood_sugar': 148,
        'systolic_bp': 155,
        'diastolic_bp': 98,
        'sex': 'M',
        'smoking': 'Y',
        'diabetes': 'Y',
        'family_history': 'Y',
        'physical_activity': 'Low'
    })
    print_result("PATIENT 1: HIGH RISK (62yr, obese, hypertensive, diabetic, smoker)", p1)

    # ============================================================
    # PATIENT 2: INTERMEDIARY RISK
    # INTERMEDIARY chance > HIGH chance (both in 40-60 range)
    # ============================================================
    p2 = predict_risk({
        'age': 52,
        'weight_kg': 85,
        'height_m': 1.72,
        'bmi': 28.7,
        'abdominal_cm': 95,
        'total_cholesterol': 220,
        'hdl': 42,
        'fasting_blood_sugar': 115,
        'systolic_bp': 135,
        'diastolic_bp': 85,
        'sex': 'M',
        'smoking': 'N',
        'diabetes': 'N',
        'family_history': 'Y',
        'physical_activity': 'Moderate'
    })
    print_result("PATIENT 2: INTERMEDIARY RISK (52yr, overweight, elevated BP, family history)", p2)
    
    # ============================================================
    # PATIENT 3: LOW RISK
    # INTERMEDIARY chance > 60%
    # ============================================================
p3 = predict_risk({
        'age': 28,
        'weight_kg': 62,
        'height_m': 1.72,
        'bmi': 21.0,
        'abdominal_cm': 74,
        'total_cholesterol': 155,
        'hdl': 72,
        'fasting_blood_sugar': 82,
        'systolic_bp': 112,
        'diastolic_bp': 72,
        'sex': 'F',
        'smoking': 'N',
        'diabetes': 'N',
        'family_history': 'N',
        'physical_activity': 'High'
    })
print_result("PATIENT 3: LOW RISK (28yr, healthy, active, no risk factors)", p3)

print("\n" + "="*50)
print("  SUMMARY")
print("="*50)
print("  Label Logic:")
print("    HIGH chance > INTERMEDIARY chance -> HIGH RISK")
print("    INTERMEDIARY chance > 60%          -> LOW RISK")
print("    Otherwise                          -> INTERMEDIARY RISK")
print("="*50)