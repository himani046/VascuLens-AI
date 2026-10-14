# VascuLens AI model artifacts

The trained binary model bundle is distributed separately because it is a generated binary artifact.

1. Download **VascuLens_AI_Retrained_Models.zip** from the ChatGPT conversation.
2. Extract it.
3. Copy `clinical.joblib` into this folder as `backend/artifacts/clinical.joblib`.
4. Install backend dependencies from `backend/requirements.txt`.
5. Start the API from the repository root with `python -m uvicorn backend.app:app --reload --port 8000`.
6. Verify `GET /api/health` reports `clinical_model_ready: true`, then check `GET /api/schema` and `GET /api/metrics`.

The `metrics.json` file contains five-fold cross-validation estimates for the retrained model selection. These are internal exploratory estimates from 303 records, not independent clinical validation. Threshold 0.5 is illustrative. LCX and RCA sensitivity is limited; do not use this prototype for diagnosis, triage, or treatment.

The `.joblib` artifact must be loaded only from a trusted source and with compatible Python/scikit-learn/XGBoost versions. Never load arbitrary user-supplied joblib files.
