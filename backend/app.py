"""Flask REST API — Sprint 3 (in progress): data upload API + pollution calculation API."""
import csv
import io
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from hpi import STANDARDS, calculate

ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__)


@app.after_request
def cors(resp):  # lets index.html call the API even when opened as a local file
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.get("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.get("/data/<path:name>")
def data(name):
    return send_from_directory(ROOT / "data", name)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/calculate")
def calc():
    try:
        return jsonify(calculate(request.get_json(force=True) or {}))
    except (ValueError, TypeError) as e:
        return jsonify(error=str(e)), 400


@app.post("/api/upload")
def upload():
    f = request.files.get("file")
    if not f or not f.filename.lower().endswith(".csv"):
        return jsonify(error="upload a .csv file in field 'file'"), 400
    rows = list(csv.DictReader(io.StringIO(f.read().decode("utf-8"))))
    results, errors = [], []
    for i, row in enumerate(rows, start=1):
        try:
            results.append({"row": i, "location": row.get("location"),
                            **calculate({k: row.get(k) for k in STANDARDS})})
        except ValueError as e:
            errors.append({"row": i, "error": str(e)})
    # TODO(next): persist to MySQL tables from db/schema.sql
    return jsonify(count=len(results), results=results, errors=errors)


if __name__ == "__main__":
    app.run(debug=True)
