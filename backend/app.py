"""FastAPI service for VascuLens AI research prototype."""
from pathlib import Path
from typing import Any
import json
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
app = FastAPI(title='VascuLens AI Research API', version='0.2.0', description='Research prototype; not a medical device.')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
                   allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['*'])

class Patient(BaseModel):
    features: dict[str, Any] = Field(..., description='Clinical feature values matching /api/schema')

def load_bundle():
    path = ROOT / 'artifacts' / 'clinical.joblib'
    return joblib.load(path) if path.exists() else None

@app.get('/api/health')
def health():
    bundle = load_bundle()
    return {'status': 'ok', 'project': 'VascuLens AI', 'clinical_model_ready': bundle is not None,
            'targets_available': list(bundle['models']) if bundle else [], 'image_model_ready': False,
            'image_model_note': 'Image segmentation is a separate experimental pathway; no patient-specific lesion model is bundled.'}

@app.get('/api/schema')
def schema():
    bundle = load_bundle()
    if not bundle:
        return {'ready': False, 'features': [], 'message': 'Train backend/train.py with the UCI extension dataset first.'}
    return {'ready': True, 'features': [{'name': name, 'default': bundle['defaults'][name],
            'type': 'number' if name in bundle['numeric'] else 'text'} for name in bundle['features']]}

@app.post('/api/predict')
def predict(patient: Patient):
    bundle = load_bundle()
    if not bundle:
        raise HTTPException(503, 'Clinical model unavailable. Train with the original UCI extension dataset first.')
    missing = [name for name in bundle['features'] if name not in patient.features]
    if missing:
        raise HTTPException(422, {'missing_features': missing})
    frame = pd.DataFrame([{name: patient.features[name] for name in bundle['features']}])
    for name in bundle['numeric']:
        frame[name] = pd.to_numeric(frame[name], errors='coerce')
    baseline = pd.DataFrame([{name: bundle['defaults'][name] for name in bundle['features']}])
    for name in bundle['numeric']:
        baseline[name] = pd.to_numeric(baseline[name], errors='coerce')
    predictions = {}
    for target, model in bundle['models'].items():
        probability = float(model.predict_proba(frame)[0, 1])
        threshold = float(bundle.get('thresholds', {}).get(target, 0.5))
        baseline_probability = float(model.predict_proba(baseline)[0, 1])
        local = []
        # One-feature-at-a-time perturbation against the median/mode reference; not SHAP and not causal.
        for feature in bundle['features']:
            if patient.features[feature] == bundle['defaults'][feature]:
                continue
            changed = baseline.copy()
            changed.loc[0, feature] = frame.loc[0, feature]
            delta = float(model.predict_proba(changed)[0, 1] - baseline_probability)
            local.append({'feature': feature, 'probability_delta_vs_reference': round(delta, 4)})
        local.sort(key=lambda item: abs(item['probability_delta_vs_reference']), reverse=True)
        predictions[target] = {'probability': round(probability, 4), 'threshold': round(threshold, 4),
            'positive_at_threshold': bool(probability >= threshold), 'reference_probability': round(baseline_probability, 4),
            'local_perturbation_top10': local[:10]}
    return {'predictions': predictions, 'explanation_method': 'single-feature perturbation vs median/mode reference; approximate, non-causal, not SHAP/LIME',
            'disclaimer': 'Research-only model scores. Not a diagnosis, treatment recommendation, or anatomical lesion localization.'}

@app.get('/api/metrics')
def metrics():
    path = ROOT / 'artifacts' / 'metrics.json'
    if not path.exists():
        raise HTTPException(503, 'No measured metrics available. Run backend/train.py with the original dataset first.')
    return json.loads(path.read_text())

@app.get('/api/explanations/global')
def global_explanations():
    path = ROOT / 'artifacts' / 'metrics.json'
    if not path.exists():
        raise HTTPException(503, 'No feature importance available until the model is trained.')
    data = json.loads(path.read_text())
    return {'targets': {target: info.get('global_permutation_importance_top15', [])
                        for target, info in data.get('targets', {}).items() if isinstance(info, dict)},
            'method': 'Permutation importance on held-out data; global descriptive importance, not causal.'}
