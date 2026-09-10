"""Modelo de riesgo de sequía (demo de hackathon).

Combina tres señales diarias en un score de 0 a 100:

- déficit de lluvia    : cuánto cae por debajo de la climatología reciente
- racha de días secos  : días consecutivos con lluvia casi nula
- anomalía térmica     : cuánto sube la temperatura sobre su media reciente

Es una aproximación didáctica, no un índice climático oficial.
"""

import numpy as np
import pandas as pd

DRY_THRESHOLD = 0.5    # mm/día por debajo del cual cuenta como "día seco"
WINDOW = 30            # ventana de 30 días para climatología
MIN_OBS = 14           # observaciones mínimas para calcular medias
STREAK_CAP = 30        # días que saturan el componente de racha

COLUMNS = [
    "date",
    "T2M",
    "PRECTOTCORR",
    "dry_streak",
    "temp_anomaly",
    "drought_risk_score",
    "risk_category",
]


def _dry_streak(precip: pd.Series) -> pd.Series:
    """Conteo de días secos consecutivos (se reinicia al llover)."""
    dry = (precip < DRY_THRESHOLD).astype(int)
    runs = (dry != dry.shift()).cumsum()
    return dry.groupby(runs).cumsum().fillna(0).astype(int)


def _rolling_mean(series: pd.Series) -> pd.Series:
    return series.rolling(WINDOW, min_periods=MIN_OBS).mean()


def _rolling_std(series: pd.Series) -> pd.Series:
    return series.rolling(WINDOW, min_periods=MIN_OBS).std()


def _precip_deficit(precip: pd.Series) -> pd.Series:
    """Fracción (0-1) en la que la lluvia cae bajo su media reciente."""
    clim = _rolling_mean(precip).replace(0, np.nan)
    deficit = (clim - precip) / clim
    return deficit.fillna(0).clip(0, 1)


def _temp_score(temp: pd.Series) -> pd.Series:
    """Z-score de la anomalía térmica, recortado a [0, 1]."""
    anom = temp - _rolling_mean(temp)
    score = anom / _rolling_std(temp).replace(0, np.nan)
    return score.replace([np.inf, -np.inf], np.nan).fillna(0).clip(0, 1)


def categorize(score: float) -> str:
    if score < 40:
        return "Bajo"
    if score < 60:
        return "Moderado"
    if score < 75:
        return "Alto"
    return "Crítico"


def compute_risk_series(df: pd.DataFrame) -> pd.DataFrame:
    """Recibe el DataFrame diario (index=fecha, columnas T2M y PRECTOTCORR)
    y devuelve la misma serie con las columnas de riesgo agregadas."""
    s = df.copy()
    precip = s["PRECTOTCORR"].clip(lower=0)
    temp = s["T2M"]

    streak_norm = np.log1p(_dry_streak(precip)) / np.log1p(STREAK_CAP)
    score = (0.45 * _precip_deficit(precip)
             + 0.30 * streak_norm.clip(0, 1)
             + 0.25 * _temp_score(temp))
    score = score.clip(0, 1) * 100

    s["dry_streak"] = _dry_streak(precip)
    s["temp_anomaly"] = (temp - _rolling_mean(temp)).round(2)
    s["drought_risk_score"] = score.round(1)
    s["risk_category"] = s["drought_risk_score"].map(categorize)

    s["temp_anomaly"] = s["temp_anomaly"].fillna(0)
    s["drought_risk_score"] = s["drought_risk_score"].fillna(0)
    s.loc[s["drought_risk_score"].isna(), "risk_category"] = "Bajo"
    return s


def records(series: pd.DataFrame) -> list[dict]:
    """Serie con riesgo -> lista de registros JSON para la API."""
    out = series.reset_index()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    cols = [c for c in COLUMNS if c in out.columns]
    return out[cols].to_dict(orient="records")


def summarize(series: pd.DataFrame) -> dict:
    """Resumen del día más reciente para el endpoint /summary."""
    last = series.iloc[-1]
    return {
        "drought_risk_score": float(last["drought_risk_score"]),
        "risk_category": str(last["risk_category"]),
        "dry_streak_days": int(last["dry_streak"]),
        "temp_anomaly_c": float(last["temp_anomaly"]),
    }