import pandas as pd
import requests
import streamlit as st

from config import (
    BASE_URL,
    POWER_BASE_URL,
    POWER_COMMUNITY,
    REQUEST_TIMEOUT,
    USE_BACKEND,
)

MISSING = -999.0  # NASA POWER usa -999.0 para datos faltantes


# --- Cliente del backend FastAPI (listo para cuando exista) -------------
@st.cache_data(ttl=300, show_spinner=False)
def get(endpoint, params=None):
    """GET hacia tu FastAPI (p. ej. /climate?lat=..&lon=..)."""
    response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60, show_spinner=False)
def post(endpoint, payload=None):
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


# --- Cliente del backend FastAPI (drought-risk) -------------------------
@st.cache_data(ttl=300, show_spinner=False)
def drought_risk_records(lat, lon, start_date, end_date):
    """Serie histórica de riesgo de sequía desde el backend FastAPI.

    Llama a GET /drought-risk?lat=..&lon=..&start_date=..&end_date=..  y
    devuelve un DataFrame con la serie diaria (T2M, PRECTOTCORR,
    drought_risk_score, risk_category, dry_streak, temp_anomaly, ...).
    """
    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")
    params = {
        "lat": round(float(lat), 4),
        "lon": round(float(lon), 4),
        "start_date": start,
        "end_date": end,
    }
    records = get("/drought-risk", params=params)

    df = pd.DataFrame(records)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")


@st.cache_data(ttl=300, show_spinner=False)
def drought_risk_summary(lat, lon, start_date, end_date):
    """Estado actual del riesgo desde el backend FastAPI.

    Llama a GET /drought-risk/summary y devuelve el resumen del día más
    reciente: score, categoría, días secos consecutivos y anomalía térmica.
    """
    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")
    params = {
        "lat": round(float(lat), 4),
        "lon": round(float(lon), 4),
        "start_date": start,
        "end_date": end,
    }
    return get("/drought-risk/summary", params=params)


# --- Datos climáticos NASA POWER ----------------------------------------
@st.cache_data(ttl=86400, show_spinner=False)  # 24 h en caché: menos llamadas
def _fetch_power(lat, lon, start, end, parameters):
    params = {
        "parameters": ",".join(parameters),
        "community": POWER_COMMUNITY,
        "latitude": lat,
        "longitude": lon,
        "start": start,
        "end": end,
        "format": "JSON",
    }
    response = requests.get(POWER_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    series = payload["properties"]["parameter"]  # {"T2M": {"20200101": 24.3, ...}, ...}
    df = pd.DataFrame(series)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "fecha"

    df = df.replace(MISSING, float("nan"))
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.interpolate(method="linear").ffill().bfill()


def fetch_climate_data(lat, lon, start_date, end_date, parameters):
    """Descarga y limpia las series diarias para un punto y un periodo dados.

    Si USE_BACKEND está activo, se puede reemplazar este bloque por
    get("/climate", {...}) y apuntar a tu FastAPI.
    """
    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")
    params = tuple(sorted(set(parameters)))
    return _fetch_power(round(float(lat), 4), round(float(lon), 4), start, end, params)