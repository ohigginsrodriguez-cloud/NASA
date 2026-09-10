import numpy as np
import pandas as pd


def monthly_aggregates(df, precip_col="PRECTOTCORR", temp_col="T2M"):
    """Series diarias -> agregado mensual (suma de lluvia, media de temperatura)."""
    cols = [c for c in (temp_col, precip_col) if c in df.columns]
    return df[cols].resample("MS").agg({temp_col: "mean", precip_col: "sum"})


def standardized_index(monthly, col, window=3):
    """SPI simplificado: z-score de la precipitación acumulada a N meses.

    Se estandariza contra la distribución histórica del mismo mes del año
    (media y desviación por mes calendario). Suficiente para un demo.
    """
    roll = monthly[col].rolling(window).sum().dropna()
    mean = roll.groupby(roll.index.month).transform("mean")
    std = roll.groupby(roll.index.month).transform("std").replace(0, np.nan)
    return (roll - mean) / std


def classify_spi(value):
    """Clasifica un valor de índice en categorías al estilo del Monitor de Sequía."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "Sin datos", "#7A8798"
    if value >= -0.5:
        return "Sin sequía", "#2E7D32"
    if value >= -0.8:
        return "Anormalmente seco", "#C4A62B"
    if value >= -1.3:
        return "Sequía moderada", "#E8871E"
    if value >= -1.6:
        return "Sequía severa", "#FC3D21"
    return "Sequía extrema", "#8E0E2F"


def drought_status(monthly, precip_col, window=3):
    """Estado actual de sequía para el último mes disponible."""
    spi = standardized_index(monthly, precip_col, window)
    current = float(spi.iloc[-1])
    label, color = classify_spi(current)
    return spi, current, label, color


def forecast_linear(series, months=3):
    """Pronóstico demo: tendencia lineal simple + banda de incertidumbre."""
    if len(series) < 6:
        return None
    x = np.arange(len(series), dtype=float)
    coef = np.polyfit(x, series.values, 1)
    resid = series.values - np.polyval(coef, x)
    sigma = float(np.std(resid)) if len(resid) > 1 else 0.0

    future = np.arange(len(series), len(series) + months, dtype=float)
    pred = np.polyval(coef, future)
    dates = pd.date_range(
        series.index[-1] + pd.offsets.MonthBegin(1), periods=months, freq="MS"
    )
    out = pd.DataFrame(
        {"valor": pred, "bajo": pred - 1.96 * sigma, "alto": pred + 1.96 * sigma},
        index=dates,
    )
    out.index.name = "fecha"
    return out


def forecast_drought_status(forecast, monthly, precip_col, window=3):
    """Clasifica la sequía esperada para cada mes del pronóstico."""
    if forecast is None:
        return []
    merged = pd.concat([monthly[precip_col], forecast["valor"]])
    roll = merged.rolling(window).sum().dropna()
    mean = roll.groupby(roll.index.month).transform("mean")
    std = roll.groupby(roll.index.month).transform("std").replace(0, np.nan)
    z = (roll - mean) / std
    z = z.loc[forecast.index]
    return [(fecha, float(v), *classify_spi(v)) for fecha, v in z.items()] if len(z) else []