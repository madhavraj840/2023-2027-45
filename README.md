# Web Application for Heavy Metal Pollution Index

**Project ID:** SKIT/CS/2023-2027/45 · **Branch:** CSE · **Section:** C · **SDG 9** — Industry, Innovation & Infrastructure
**Mentor:** Vinod Kataria

| Member | Role | Sprint |
|---|---|---|
| Krishna Meena | Team Lead, ML | ML + Integration of Models |
| Manish | Research & Analysis | Data Validation + Analysis |
| Madhav Raj | App Development | Backend + API + DB |
| Manogya Chopra | Frontend | Frontend + API + Maps + Dashboard |

**Stack:** React (frontend) · Flask (REST API) · Python (ML) · MySQL (storage)

## Progress (as of 18/09/2026)

| User story | Owner | Dates | Status | Where |
|---|---|---|---|---|
| Dataset finalization & preprocessing | Krishna | 10/8 – 22/8 | ✅ Done | `ml/preprocess.py` |
| Dataset preparation module | Manish | 10/8 – 22/8 | ✅ Done | `ml/preprocess.py`, `data/` |
| Database development | Madhav | 10/8 – 22/8 | ✅ Done | `db/schema.sql` |
| UI modules development | Manogya | 10/8 – 22/8 | ✅ Done | `index.html` |
| Pollution index calculation (HPI, NPI) | Manish | 17/8 – 3/10 | 🟡 In progress | `backend/hpi.py` |
| Data upload API | Madhav | 17/8 – 3/10 | 🟡 In progress | `backend/app.py` → `POST /api/upload` |
| Pollution calculation API | Madhav | 17/8 – 31/10 | 🟡 In progress | `backend/app.py` → `POST /api/calculate` |
| Dashboard development | Manogya | 17/8 – 3/10 | 🟡 In progress | `index.html` (calculator + charts) |
| ML model development | Krishna | 24/8 – 3/10 | 🟡 In progress | labels generated in `data/processed_samples.csv` |

> `data/sample_water_samples.csv` is a small **sample dataset for development/testing**, not real field data. It will be replaced by the finalized source dataset.

## Run

```bash
pip install -r requirements.txt
python backend/hpi.py          # self-check of index formulas
python ml/preprocess.py        # clean dataset -> data/processed_samples.csv
python backend/app.py          # API on http://127.0.0.1:5000
mysql -u root -p < db/schema.sql
```

Open `index.html` in a browser for the calculator UI.

## API

- `GET /api/health`
- `POST /api/calculate` — JSON `{"pb": 0.02, "as": 0.005}` → `{"hpi", "npi", "hpi_class"}`
- `POST /api/upload` — multipart `file=<csv>` → per-row indices

## Formulas

- HPI = Σ(Wᵢ·Qᵢ)/ΣWᵢ, Wᵢ = 1/Sᵢ, Qᵢ = 100·(Mᵢ − Iᵢ)/(Sᵢ − Iᵢ) (Mohan et al., 1996)
- NPI = √[(P̄² + P²max)/2], Pᵢ = Cᵢ/Sᵢ (Nemerow, 1974)
- Standards: WHO / BIS IS 10500
