export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface ClinicalFormData {
  age: number;
  gender: 'M' | 'F';
  height_cm: number;
  weight_kg: number;
  systolic_bp: number;
  diastolic_bp: number;
  total_cholesterol: number;
  hdl: number;
  fasting_blood_sugar: number;
  smoking_status: 'Y' | 'N';
  diabetes_status: 'Y' | 'N';
  physical_activity: 'Low' | 'Moderate' | 'High';
  family_history_cvd: 'Y' | 'N';
  patient_name?: string;
}

export interface PredictionResponse {
  patient_id: string;
  risk_score: number;
  risk_level: string;
  confidence: string;
  source: string;
  timestamp: string;
  risk_explanation?: string;   // LLM natural language explanation of SHAP/Grad-CAM
  explanation: {
    shap: Record<string, number> | null;
    gradcam: string | null;  // base64
  };
  recommendations: {
    diet: string;
    exercise: string;
    medical_guidance: string;
    powered_by?: string;
  };
}

export interface HistoryItem {
  id: number;
  patient_name: string | null;
  risk_score: number;
  risk_level: string;
  confidence: string;
  source: string;
  created_at: string;
}
