"""Flask API that serves the trained PLI model.   Run:  python backend_app.py"""
import json
import math
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request

from gw_utils import GW_FEATURES, GW_MAX_DISTANCE_KM, gw_features_for_points, risk_class

BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "models" / "best_model.joblib"
META_FILE = BASE_DIR / "models" / "model_meta.json"
STATION_FILE = BASE_DIR / "data" / "processed" / "gw_station_table.csv"

app = Flask(__name__)
_state = {"model": None, "meta": None, "stations": None}

REQUIRED = ["latitude", "longitude", "land_use", "soil_pH", "organic_carbon_pct"]
LIMITS = {"latitude": (20.0, 32.0), "longitude": (68.0, 80.0),
          "soil_pH": (3.0, 11.0), "organic_carbon_pct": (0.0, 20.0)}
MAX_BATCH = 1000


class ValidationError(ValueError):
    pass


def load_artifacts():
    if _state["model"] is None:
        if not MODEL_FILE.exists() or not META_FILE.exists() or not STATION_FILE.exists():
            raise FileNotFoundError("Model files not found. Run the notebook (Task 1-3) first.")
        _state["model"] = joblib.load(MODEL_FILE)
        with open(META_FILE, encoding="utf-8") as f:
            _state["meta"] = json.load(f)
        _state["stations"] = pd.read_csv(STATION_FILE)


def _to_float(payload, key):
    try:
        val = float(payload[key])
    except (TypeError, ValueError):
        raise ValidationError(f"'{key}' must be a number")
    if math.isnan(val) or math.isinf(val):
        raise ValidationError(f"'{key}' must be a finite number")
    return val


def build_feature_frame(samples):
    land_uses = _state["meta"]["land_use_categories"]
    rows = []
    for i, s in enumerate(samples):
        if not isinstance(s, dict):
            raise ValidationError(f"sample {i}: must be a JSON object")
        missing = [k for k in REQUIRED if k not in s]
        if missing:
            raise ValidationError(f"sample {i}: missing field(s) {missing}")
        row = {}
        try:
            for k in ("latitude", "longitude", "soil_pH", "organic_carbon_pct"):
                row[k] = _to_float(s, k)
                lo, hi = LIMITS[k]
                if not lo <= row[k] <= hi:
                    raise ValidationError(f"'{k}' must be between {lo} and {hi}")
            lu = str(s["land_use"]).strip().title()
            if lu not in land_uses:
                raise ValidationError(f"'land_use' must be one of {land_uses}")
            row["land_use"] = lu
            for g in GW_FEATURES:  # optional manual groundwater override
                row["_user_" + g] = _to_float(s, g) if s.get(g) is not None else None
        except ValidationError as e:
            raise ValidationError(f"sample {i}: {e}")
        rows.append(row)

    df = pd.DataFrame(rows)
    gw = gw_features_for_points(df["latitude"], df["longitude"], _state["stations"])
    for g in GW_FEATURES:
        user = df["_user_" + g].astype(float)
        df[g] = user.where(user.notna(), gw[g])
    df["gw_nearest_km"] = gw["gw_nearest_km"]
    df["_gw_stations_used"] = gw["gw_stations_used"]
    return df


def predict_samples(samples):
    load_artifacts()
    df = build_feature_frame(samples)
    preds = _state["model"].predict(df[_state["meta"]["features"]])
    out = []
    for i, p in enumerate(preds):
        p = max(0.0, float(p))  # PLI cannot be negative
        warnings = []
        if df.loc[i, "_gw_stations_used"] == 0:
            warnings.append(f"No groundwater station within {GW_MAX_DISTANCE_KM:.0f} km; "
                            "groundwater features were imputed with training medians.")
        near = df.loc[i, "gw_nearest_km"]
        out.append({"predicted_PLI": round(p, 4), "risk_class": risk_class(p), "polluted": bool(p > 1),
                    "nearest_groundwater_station_km": None if pd.isna(near) else round(float(near), 2),
                    "warnings": warnings})
    return out


@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@app.errorhandler(ValidationError)
def handle_validation(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(404)
def handle_404(e):
    return jsonify(error="not found"), 404


@app.errorhandler(405)
def handle_405(e):
    return jsonify(error="method not allowed"), 405


@app.errorhandler(Exception)
def handle_unexpected(e):
    app.logger.exception("unexpected error")
    return jsonify(error="internal server error", detail=str(e)), 500


@app.get("/")
def index():
    return jsonify(service="Soil + Groundwater heavy-metal index (PLI) prediction API",
                   endpoints=["/health", "/model-info", "/predict", "/predict/batch"])


@app.get("/health")
def health():
    try:
        load_artifacts()
        return jsonify(status="ok", model_loaded=True)
    except FileNotFoundError as e:
        return jsonify(status="error", model_loaded=False, detail=str(e)), 503


@app.get("/model-info")
def model_info():
    load_artifacts()
    m = _state["meta"]
    return jsonify(model_name=m["model_name"], target=m["target"], required_fields=REQUIRED,
                   optional_fields=GW_FEATURES, land_use_values=m["land_use_categories"],
                   test_metrics=m["test_metrics"], all_models_test_r2=m["all_models_test_r2"],
                   leave_one_area_out_metrics=m["leave_one_area_out_metrics"], note=m["note"])


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError("body must be a JSON object")
    return jsonify(predict_samples([payload])[0])


@app.post("/predict/batch")
def predict_batch():
    payload = request.get_json(silent=True)
    samples = payload.get("samples") if isinstance(payload, dict) else payload
    if not isinstance(samples, list) or not samples:
        raise ValidationError('body must be a non-empty JSON list or {"samples": [...]}')
    if len(samples) > MAX_BATCH:
        raise ValidationError(f"maximum batch size is {MAX_BATCH}")
    results = predict_samples(samples)
    return jsonify(count=len(results), predictions=results)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
