"""Train leakage-aware clinical CAD and vessel classifiers on the UCI extension dataset.

Example: python train.py --data '/path/to/extention of Z-Alizadeh sani dataset.xlsx'
The dataset is not bundled. Outputs are saved under backend/artifacts/.
"""
from __future__ import annotations
import argparse, json, re, warnings
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, recall_score, precision_score,
    f1_score, roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix)
from sklearn.inspection import permutation_importance

ROOT = Path(__file__).resolve().parent
SEED = 42
TARGETS = {'CAD': ('CAD', 'Cath'), 'LAD': ('LAD',), 'LCX': ('LCX',), 'RCA': ('RCA',)}
EXCLUDED_NORMALIZED = {re.sub(r'[^a-z0-9]', '', x.lower()) for x in
    ('CAD', 'Cath', 'LAD', 'LCX', 'RCA', 'ID', 'patient_id', 'patientid')}


def norm(value: object) -> str:
    return re.sub(r'[^a-z0-9]', '', str(value).lower())


def find_col(df: pd.DataFrame, options: tuple[str, ...]) -> str | None:
    for option in options:
        found = next((c for c in df.columns if norm(c) == norm(option)), None)
        if found is not None:
            return found
    return None


def encode_target(series: pd.Series) -> pd.Series:
    """Map known CAD/stenosis labels to 0/1; fail loudly on unknown labels."""
    values = series.astype(str).str.strip().str.lower()
    unique = set(values.unique())
    if unique <= {'0', '1', '0.0', '1.0'}:
        return values.astype(float).astype(int)
    positive = {'cad', 'yes', 'positive', 'present', 'disease', 'stenosis', 'stenotic', '1', 'true', 'abnormal'}
    negative = {'normal', 'no', 'negative', 'absent', 'healthy', '0', 'false', 'non-cad', 'noncad', 'non stenotic', 'nonstenotic'}
    if unique <= positive | negative:
        return values.isin(positive).astype(int)
    raise ValueError(f'Unknown target labels {sorted(unique)}. Add an explicit mapping; do not guess.')


def make_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric = X.select_dtypes(include=['number', 'bool']).columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    transformers = []
    if numeric:
        transformers.append(('num', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), numeric))
    if categorical:
        transformers.append(('cat', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
            ('encode', OneHotEncoder(handle_unknown='ignore'))]), categorical))
    return ColumnTransformer(transformers, remainder='drop')


def build_candidates(X: pd.DataFrame) -> dict[str, object]:
    return {
        'LogisticRegression': LogisticRegression(max_iter=3000, class_weight='balanced', C=0.5, random_state=SEED),
        'RBF_SVM': SVC(C=1.0, kernel='rbf', probability=True, class_weight='balanced', random_state=SEED),
        'ExtraTrees': ExtraTreesClassifier(n_estimators=250, min_samples_leaf=2, max_features='sqrt', class_weight='balanced', random_state=SEED, n_jobs=1),
        'RandomForest': RandomForestClassifier(n_estimators=250, min_samples_leaf=2, max_features='sqrt', class_weight='balanced', random_state=SEED, n_jobs=1),
    }


def metric_pack(y_true: pd.Series, prob: np.ndarray, threshold: float) -> dict:
    pred = (prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        'threshold': round(float(threshold), 4),
        'accuracy': round(float(accuracy_score(y_true, pred)), 4),
        'balanced_accuracy': round(float(balanced_accuracy_score(y_true, pred)), 4),
        'precision': round(float(precision_score(y_true, pred, zero_division=0)), 4),
        'sensitivity_recall': round(float(recall_score(y_true, pred, zero_division=0)), 4),
        'specificity': round(float(tn / (tn + fp)) if tn + fp else float('nan'), 4),
        'f1': round(float(f1_score(y_true, pred, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_true, prob)), 4) if len(np.unique(y_true)) == 2 else None,
        'average_precision': round(float(average_precision_score(y_true, prob)), 4),
        'brier_score': round(float(brier_score_loss(y_true, prob)), 4),
        'confusion_matrix': {'TN': int(tn), 'FP': int(fp), 'FN': int(fn), 'TP': int(tp)},
    }


def main(path: str) -> None:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f'Dataset not found: {source}')
    df = pd.read_csv(source) if source.suffix.lower() == '.csv' else pd.read_excel(source)
    df.columns = [str(c).strip().replace('\ufeff', '') for c in df.columns]
    if len(df) < 30:
        raise ValueError(f'Expected the original clinical dataset; only {len(df)} rows found.')
    target_columns = {target: find_col(df, options) for target, options in TARGETS.items()}
    if target_columns['CAD'] is None:
        raise ValueError('CAD target not found. Expected a CAD column or Cath angiography result.')
    if target_columns['LAD'] is None or target_columns['LCX'] is None or target_columns['RCA'] is None:
        warnings.warn('One or more vessel labels are absent. Only available targets will be trained.')
    feature_columns = [c for c in df.columns if norm(c) not in EXCLUDED_NORMALIZED and not norm(c).startswith('unnamed')]
    X_all = df[feature_columns].copy()
    for col in X_all.columns:
        if X_all[col].dtype == 'object':
            converted = pd.to_numeric(X_all[col], errors='coerce')
            if X_all[col].notna().sum() and converted.notna().sum() >= 0.95 * X_all[col].notna().sum():
                X_all[col] = converted
    output = {'project': 'VascuLens AI', 'dataset_file': source.name, 'dataset_rows': int(len(df)),
              'feature_count': len(feature_columns), 'features': feature_columns,
              'excluded_from_features': sorted(EXCLUDED_NORMALIZED), 'targets': {},
              'validation': 'Stratified 80/20 holdout; model selection uses training-only stratified CV. External validation required.',
              'clinical_warning': 'Research/education only; not a diagnosis or substitute for diagnostic imaging.'}
    defaults = {}
    for col in feature_columns:
        series = X_all[col]
        if pd.api.types.is_numeric_dtype(series):
            defaults[col] = float(series.median()) if series.notna().any() else 0.0
        else:
            mode = series.dropna().mode()
            defaults[col] = str(mode.iloc[0]) if not mode.empty else ''
    models, thresholds = {}, {}
    for target, col in target_columns.items():
        if col is None:
            continue
        mask = df[col].notna()
        X = X_all.loc[mask].reset_index(drop=True)
        y = encode_target(df.loc[mask, col]).reset_index(drop=True)
        counts = y.value_counts()
        if y.nunique() != 2 or int(counts.min()) < 5:
            output['targets'][target] = {'error': 'Insufficient examples in both classes', 'class_counts': {str(k): int(v) for k, v in counts.items()}}
            continue
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
        cv = StratifiedKFold(n_splits=min(5, int(y_train.value_counts().min())), shuffle=True, random_state=SEED)
        scores = []
        for name, estimator in build_candidates(X_train).items():
            pipeline = Pipeline([('preprocessor', make_preprocessor(X_train)), ('classifier', estimator)])
            try:
                vals = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring='roc_auc', n_jobs=1)
                scores.append((float(vals.mean()), float(vals.std()), name, pipeline))
            except Exception as exc:
                output['targets'].setdefault(target, {}).setdefault('candidate_failures', {})[name] = f'{type(exc).__name__}: {exc}'
        if not scores:
            output['targets'][target] = {'error': 'All model candidates failed'}
            continue
        cv_auc, cv_sd, name, model = max(scores, key=lambda entry: entry[0])
        oof = cross_val_predict(model, X_train, y_train, cv=cv, method='predict_proba', n_jobs=1)[:, 1]
        threshold_grid = np.linspace(0.2, 0.8, 61)
        threshold = max(((balanced_accuracy_score(y_train, oof >= t), t) for t in threshold_grid), key=lambda z: z[0])[1]
        model.fit(X_train, y_train)
        prob = model.predict_proba(X_test)[:, 1]
        metrics = metric_pack(y_test, prob, float(threshold))
        try:
            pi = permutation_importance(model, X_test, y_test, n_repeats=4, random_state=SEED, scoring='roc_auc', n_jobs=1)
            importance = sorted([{'feature': str(f), 'mean_auc_drop': round(float(v), 5)} for f, v in zip(X_test.columns, pi.importances_mean)], key=lambda v: v['mean_auc_drop'], reverse=True)[:15]
        except Exception as exc:
            importance = []
            output['targets'].setdefault(target, {})['importance_warning'] = str(exc)
        output['targets'].setdefault(target, {}).update({'target_column': col, 'selected_model': name,
            'class_counts': {str(k): int(v) for k, v in y.value_counts().items()}, 'training_cv_roc_auc_mean': round(cv_auc, 4),
            'training_cv_roc_auc_sd': round(cv_sd, 4), 'train_n': len(y_train), 'holdout_n': len(y_test),
            'holdout': metrics, 'global_permutation_importance_top15': importance,
            'note': 'Model probabilities are not clinical calibration or confirmed stenosis.'})
        models[target] = model
        thresholds[target] = float(threshold)
    if not models:
        raise RuntimeError('No targets were trained; verify dataset target columns and labels.')
    out = ROOT / 'artifacts'
    out.mkdir(parents=True, exist_ok=True)
    numeric_features = X_all.select_dtypes(include=['number', 'bool']).columns.tolist()
    joblib.dump({'models': models, 'features': feature_columns, 'numeric': numeric_features, 'defaults': defaults, 'thresholds': thresholds}, out / 'clinical.joblib')
    (out / 'metrics.json').write_text(json.dumps(output, indent=2, allow_nan=False))
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, help='Path to original UCI CSV/XLSX; do not commit patient data.')
    main(parser.parse_args().data)
