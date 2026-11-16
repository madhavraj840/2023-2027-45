# Soil + Groundwater PLI Prediction (Jupyter Notebook project)

Main file: **Soil_GW_PLI_Project.ipynb** (already contains outputs; you can re-run it).
Models: Linear Regression (LR), Random Forest (RF), SVM (SVR), ANN (MLP).

## Run on your computer (Windows / Mac / Linux)
Python 3.9+ required.

1. Unzip this folder (Extract All on Windows).
2. Open a terminal INSIDE the folder (Windows: type `cmd` in the folder address bar and press Enter).
3. Run:
```
python -m venv venv
venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
jupyter notebook
```
4. In the browser open `Soil_GW_PLI_Project.ipynb` -> menu **Kernel -> Restart & Run All**
   (about 2-6 minutes). Or use VS Code: open the folder, open the .ipynb, click "Run All".
5. Start the API (new terminal, same folder, venv active):
```
python backend_app.py
```
   Open http://127.0.0.1:5000/health

`backend_app.py` and `gw_utils.py` are created by the notebook itself. They are already included here.

## Notebook sections = sprint timeline
| Task | Dates |
|---|---|
| Task 1 Dataset finalisation & preprocessing | 10/08/2026 - 22/08/2026 |
| Task 2 ML model development (LR, RF, SVM, ANN) | 24/08/2026 - 03/10/2026 |
| Task 3 Training, tuning & evaluation | 14/09/2026 - 21/10/2026 |
| Task 4 ML-backend integration (Flask API) | 13/10/2026 - 02/01/2027 |

## Notes
* Soil data is SIMULATED; the groundwater file has no heavy metals, so groundwater general chemistry is joined by location (nearest stations).
* Metal concentrations are not model inputs (PLI is computed from them = data leakage).
* Run the notebook from the folder that contains `data/raw/`.
