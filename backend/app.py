"""Flask REST API — Sprint 3 (in progress): data upload API + pollution calculation API."""
import csv
import io

from flask import Flask, jsonify, request

from hpi import STANDARDS, calculate

app = Flask(__name__)


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
