# CVD Risk Prediction Web Application

Full-stack web app for cardiovascular disease risk prediction using:
- **Clinical model** — XGBoost (81.30% accuracy)
- **Retinal model** — Hybrid CNN + ViT (75.34% accuracy, AUC 82.95%)
- **Fusion** — Weighted average (0.6 × clinical + 0.4 × retinal)

---

## Project Structure

```
webapp/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── routers/  # auth.py, predict.py
│   │   ├── services/ # clinical, retinal, recommendation
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── auth.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
└── frontend/         # React + TypeScript + Tailwind
    ├── src/
    │   ├── pages/    # Landing, Login, Signup, Dashboard, Assessment, Result, History
    │   ├── components/ # Navbar, RiskGauge, SHAPChart, GradCAMImage, Recommendations
    │   ├── api/      # axios client
    │   ├── context/  # AuthContext
    │   └── types/    # TypeScript types
    ├── package.json
    └── .env
```

---

## Backend Setup

### 1. Create and activate virtual environment
```bash
cd webapp/backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

If you have the retinal model, also install:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install timm
```

### 3. Configure environment variables
Edit `webapp/backend/.env`:
```
DATABASE_URL=sqlite:///./cvd.db
SECRET_KEY=your_super_secret_key_min32chars_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
MODEL_PATH=../../data/processed/best_model.pkl
SCALER_PATH=../../data/processed/scaler.pkl
RETINAL_MODEL_PATH=../../models/retinal/hybrid_model.pth
UPLOAD_DIR=uploads/
```

### 4. Run the backend
```bash
cd webapp/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

---

## Frontend Setup

### 1. Install Node.js dependencies
```bash
cd webapp/frontend
npm install
```

### 2. Configure environment variables
Edit `webapp/frontend/.env`:
```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id
```

### 3. Run the frontend
```bash
npm run dev
```

Frontend available at: http://localhost:3000

---

## Google OAuth Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project → APIs & Services → Credentials
3. Create OAuth 2.0 Client ID (Web Application)
4. Add `http://localhost:3000` to Authorized JavaScript origins
5. Add `http://localhost:8000` to Authorized redirect URIs
6. Copy Client ID and Secret to both `.env` files

---

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /auth/signup | Register with email/password | No |
| POST | /auth/login | Login → JWT token | No |
| POST | /auth/google | Google OAuth login | No |
| GET | /auth/me | Get current user | Yes |
| POST | /predict/fusion | Full prediction (clinical + optional retinal) | Yes |
| GET | /predict/history | User's prediction history | Yes |
| GET | /predict/{id} | Specific prediction | Yes |
| GET | /health | Health check | No |

---

## Risk Level Thresholds

| Probability of HIGH | Label |
|---------------------|-------|
| < 30% | LOW RISK |
| 30% – 70% | INTERMEDIARY RISK |
| > 70% | HIGH RISK |

---

## Notes

- The retinal model requires PyTorch and timm. If not installed, clinical-only predictions still work.
- SQLite is used for development. For production, set `DATABASE_URL` to a PostgreSQL connection string.
- PDF reports are generated client-side using jsPDF.
- SHAP explanations are computed server-side and returned as a feature-importance dictionary.
- Grad-CAM heatmaps are returned as base64-encoded PNG images.
