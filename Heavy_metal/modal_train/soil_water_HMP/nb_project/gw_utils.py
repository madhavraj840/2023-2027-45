"""Helpers shared by the notebook and the backend API."""
import numpy as np
import pandas as pd

GW_MAX_DISTANCE_KM = 50.0   # search radius soil point <-> groundwater station
GW_K_NEAREST = 5            # neighbours used in inverse-distance weighting

# column-name prefix in raw CGWB file -> short feature name
GW_COLUMN_PREFIXES = {
    "Potential of Hydrogen": "gw_pH",
    "Electric Conductivity": "gw_EC",
    "Carbonate": "gw_CO3",
    "Bicarbonate": "gw_HCO3",
    "Total Alkalinity": "gw_Alkalinity",
    "Chloride": "gw_Cl",
    "Sulphate": "gw_SO4",
    "Total Hardness": "gw_Hardness",
    "Calcium": "gw_Ca",
    "Magnesium": "gw_Mg",
    "Sodium": "gw_Na",
    "Iron": "gw_Fe",
}
GW_FEATURES = list(GW_COLUMN_PREFIXES.values())

# physically plausible limits; values outside are unit / entry errors -> NaN
GW_LIMITS = {
    "gw_pH": (5.0, 10.0), "gw_EC": (50.0, 40000.0), "gw_CO3": (0.0, 500.0),
    "gw_HCO3": (0.0, 3000.0), "gw_Alkalinity": (0.0, 3000.0), "gw_Cl": (0.0, 15000.0),
    "gw_SO4": (0.0, 10000.0), "gw_Hardness": (10.0, 10000.0), "gw_Ca": (0.0, 2000.0),
    "gw_Mg": (0.0, 1500.0), "gw_Na": (0.0, 10000.0), "gw_Fe": (0.0, 50.0),
}


def read_csv_safe(path):
    """Read a CSV with UTF-8, fall back to latin-1."""
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


def risk_class(pli):
    """Conventional PLI classes (PLI > 1 = soil quality deteriorating)."""
    if pli <= 1:
        return "Low (PLI <= 1)"
    if pli <= 2:
        return "Moderate (1 < PLI <= 2)"
    if pli <= 3:
        return "High (2 < PLI <= 3)"
    return "Very high (PLI > 3)"


def _haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1 = np.radians(lat1)[:, None], np.radians(lon1)[:, None]
    lat2, lon2 = np.radians(lat2)[None, :], np.radians(lon2)[None, :]
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def gw_features_for_points(lat, lon, stations, k=GW_K_NEAREST,
                           max_km=GW_MAX_DISTANCE_KM, chunk=500):
    """Inverse-distance-weighted groundwater chemistry at arbitrary points.

    Returns DataFrame: GW_FEATURES + gw_nearest_km + gw_stations_used.
    """
    lat = np.atleast_1d(np.asarray(lat, dtype=float))
    lon = np.atleast_1d(np.asarray(lon, dtype=float))
    s_lat = stations["latitude"].to_numpy(dtype=float)
    s_lon = stations["longitude"].to_numpy(dtype=float)
    s_vals = stations[GW_FEATURES].to_numpy(dtype=float)
    k = min(k, len(stations))

    out_vals = np.full((len(lat), len(GW_FEATURES)), np.nan)
    nearest = np.full(len(lat), np.nan)
    used = np.zeros(len(lat), dtype=int)
    for start in range(0, len(lat), chunk):
        sl = slice(start, start + chunk)
        D = _haversine_km(lat[sl], lon[sl], s_lat, s_lon)
        idx = np.argsort(D, axis=1)[:, :k]
        d = np.take_along_axis(D, idx, axis=1)
        valid = d <= max_km
        vals = s_vals[idx]
        w = np.where(valid, 1.0 / np.maximum(d, 0.5) ** 2, 0.0)
        w3 = w[:, :, None] * (~np.isnan(vals))
        num = np.nansum(np.where(np.isnan(vals), 0.0, vals) * w3, axis=1)
        den = w3.sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            res = np.where(den > 0, num / den, np.nan)
        out_vals[sl] = res
        nearest[sl] = d[:, 0]
        used[sl] = valid.sum(axis=1)
    out = pd.DataFrame(out_vals, columns=GW_FEATURES)
    out["gw_nearest_km"] = nearest
    out["gw_stations_used"] = used
    return out
