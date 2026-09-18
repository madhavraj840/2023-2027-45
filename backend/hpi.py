"""Heavy-metal pollution indices (HPI, Nemerow). Same standards/formulas as index.html."""
import math

# symbol: (standard limit S, ideal value I) in mg/L — WHO / BIS IS 10500
STANDARDS = {
    "as": (0.01, 0), "cd": (0.003, 0), "cr": (0.05, 0), "cu": (2.0, 0.05),
    "fe": (0.3, 0.1), "pb": (0.01, 0), "mn": (0.1, 0.05), "ni": (0.02, 0),
    "zn": (3.0, 0.1), "hg": (0.001, 0),
}


def hpi_class(hpi):
    for limit, label in ((10, "Excellent"), (25, "Good"), (50, "Moderate"), (100, "Poor")):
        if hpi < limit:
            return label
    return "Very Poor / Critical"


def calculate(sample):
    """sample: {metal: concentration mg/L}; missing/None metals are skipped."""
    m = {k: float(v) for k, v in sample.items() if k in STANDARDS and v not in (None, "")}
    if not m:
        raise ValueError("no valid metal concentrations")
    w = {k: 1 / STANDARDS[k][0] for k in m}
    q = {k: max(0.0, 100 * (m[k] - STANDARDS[k][1]) / (STANDARDS[k][0] - STANDARDS[k][1])) for k in m}
    hpi = sum(w[k] * q[k] for k in m) / sum(w.values())
    p = [m[k] / STANDARDS[k][0] for k in m]
    npi = math.sqrt(((sum(p) / len(p)) ** 2 + max(p) ** 2) / 2)
    return {"hpi": round(hpi, 2), "npi": round(npi, 3), "hpi_class": hpi_class(hpi)}


if __name__ == "__main__":
    r = calculate({"pb": 0.01})  # exactly at the limit -> HPI 100
    assert r["hpi"] == 100 and r["npi"] == 1.0, r
    assert calculate({"as": 0.001, "zn": 0.1})["hpi_class"] == "Excellent"
    print("hpi.py self-check passed")
