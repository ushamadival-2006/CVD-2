import requests

# Your token from the previous step
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzg0MDE2MDAxfQ.PQEAP5dmbhs-0BiWLcth3YfKBLkojCZsRuv54WWqBCo"

headers = {"Authorization": f"Bearer {token}"}

data = {
    "age": 55,
    "gender": "M",
    "height_cm": 175,
    "weight_kg": 85,
    "systolic_bp": 140,
    "diastolic_bp": 90,
    "total_cholesterol": 220,
    "hdl": 45,
    "fasting_blood_sugar": 115,
    "smoking_status": 1,
    "diabetes_status": 0,
    "physical_activity": 1,
    "family_history_cvd": 1,
    "patient_name": "Test"
}

response = requests.post(
    "http://127.0.0.1:8000/predict/fusion",
    headers=headers,
    data=data
)

print(response.json())