"""
Rule-based recommendation engine.
Generates personalised diet, exercise, and medical guidance
based on risk score and clinical inputs.
"""

def get_recommendations(risk_score: float, clinical: dict) -> dict:
    bmi        = clinical.get('weight_kg', 70) / ((clinical.get('height_cm', 170) / 100) ** 2)
    age        = clinical.get('age', 50)
    smoking    = clinical.get('smoking_status', 'N') == 'Y'
    diabetes   = clinical.get('diabetes_status', 'N') == 'Y'
    family     = clinical.get('family_history_cvd', 'N') == 'Y'
    systolic   = clinical.get('systolic_bp', 120)
    activity   = clinical.get('physical_activity', 'Moderate')
    cholesterol= clinical.get('total_cholesterol', 200)

    # ── Diet ──────────────────────────────────────────────────────────────────
    if risk_score >= 70:
        diet = (
            "High-risk diet plan: Follow a strict heart-healthy diet. "
            "Eliminate processed foods, trans fats, and excess sodium (<1500 mg/day). "
            "Adopt the DASH or Mediterranean diet — rich in vegetables, fruits, whole grains, "
            "legumes, fatty fish (salmon, mackerel), nuts, and olive oil. "
            "Limit red meat to ≤1 serving/week. Target cholesterol <150 mg/dL through diet."
        )
        if bmi >= 30:
            diet += " Your BMI indicates obesity — aim for a 500–700 calorie daily deficit under dietitian supervision."
        if diabetes:
            diet += " Strictly limit simple sugars and refined carbohydrates; monitor glycaemic index of all foods."
    elif risk_score >= 30:
        diet = (
            "Moderate-risk diet plan: Adopt a heart-healthy Mediterranean-style diet. "
            "Increase intake of vegetables (5+ servings/day), fruits (2–3 servings/day), "
            "whole grains, and omega-3-rich fish (2x/week). "
            "Reduce saturated fats, processed meats, and sugary beverages. "
            "Limit sodium to <2000 mg/day."
        )
        if cholesterol >= 200:
            diet += " Your cholesterol is elevated — include oats, flaxseed, and plant sterols."
    else:
        diet = (
            "Low-risk diet plan: Maintain your current healthy habits. "
            "Continue eating a balanced diet with plenty of vegetables, fruits, whole grains, "
            "lean proteins, and healthy fats. Stay hydrated (8+ glasses of water/day). "
            "Limit processed foods and excess sugar as a preventive measure."
        )

    # ── Exercise ──────────────────────────────────────────────────────────────
    if risk_score >= 70:
        exercise = (
            "High-risk exercise plan: Begin supervised cardiac rehabilitation if possible. "
            "Start with low-intensity walking 20–30 minutes, 3–5 days/week, "
            "gradually increasing to 150 minutes/week of moderate aerobic activity. "
            "Avoid high-intensity exercise without medical clearance. "
            "Include gentle stretching and breathing exercises daily."
        )
        if age >= 60:
            exercise += " At your age, add balance exercises (chair yoga, tai chi) to reduce fall risk."
    elif risk_score >= 30:
        exercise = (
            "Moderate-risk exercise plan: Aim for 150–300 minutes/week of moderate aerobic exercise. "
            "Recommended activities: brisk walking, cycling, swimming, or dancing. "
            "Add 2 strength-training sessions/week (light weights or resistance bands). "
        )
        if activity == 'Low':
            exercise += " Since your current activity level is low, start with 10-minute walks and increase by 5 minutes each week."
    else:
        exercise = (
            "Low-risk exercise plan: Maintain at least 150 minutes/week of moderate physical activity. "
            "Mix cardio (running, cycling, swimming) with strength training 2–3x/week. "
            "Include flexibility and mobility work. Stay active throughout the day — take stairs, walk more."
        )

    # ── Medical Guidance ──────────────────────────────────────────────────────
    if risk_score >= 70:
        medical = (
            "HIGH RISK — Urgent medical attention recommended. "
            "Please consult a cardiologist within the next 1–2 weeks for a comprehensive cardiovascular evaluation. "
            "Request: lipid panel, ECG, echocardiogram, and stress test. "
        )
        if systolic >= 140:
            medical += "Your blood pressure is in Stage 2 hypertension — blood pressure medication may be required. "
        if family:
            medical += "Family history of CVD significantly elevates your risk — genetic counselling and early intervention are advised. "
        if smoking:
            medical += "SMOKING CESSATION IS CRITICAL — ask your doctor about nicotine replacement therapy or varenicline. "
    elif risk_score >= 30:
        medical = (
            "INTERMEDIARY RISK — Schedule a check-up with your GP within the next month. "
            "Request: fasting lipid panel, blood glucose, blood pressure monitoring. "
            "Discuss preventive strategies and whether statin therapy is appropriate. "
        )
        if diabetes:
            medical += "With diabetes, ensure HbA1c is checked every 3 months and target HbA1c < 7%. "
        if systolic >= 130:
            medical += "Your blood pressure is elevated — monitor at home and discuss treatment options with your doctor. "
    else:
        medical = (
            "LOW RISK — Continue annual health check-ups with your GP. "
            "Monitor blood pressure, cholesterol, and blood sugar annually. "
            "Maintain healthy lifestyle habits. "
        )
        if family:
            medical += "Despite low current risk, your family history warrants regular cardiovascular screenings. "

    return {"diet": diet, "exercise": exercise, "medical_guidance": medical}
