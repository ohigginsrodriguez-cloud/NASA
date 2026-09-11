"""Fachada del modelo de predicción de sequía (demo).

El modelo vive en ``drought_risk.py``. Este módulo lo expone bajo los
nombres ``calculate_drought_risk`` y ``get_current_risk_summary`` para
que el resto del proyecto no tenga que conocer la implementación interna.
"""

try:
    from backend.drought_risk import compute_risk_series, summarize
except ModuleNotFoundError:
    from drought_risk import compute_risk_series, summarize


def calculate_drought_risk(df):
    return compute_risk_series(df)


def get_current_risk_summary(df):
    resumen = summarize(df)
    resumen["date"] = (
        str(df.index[-1].date()) if hasattr(df.index[-1], "date") else None
    )
    return resumen


if __name__ == "__main__":
    try:
        from backend.nasa_power_client import get_power_data
        from backend.preprocessing import preprocess_power_data
    except ModuleNotFoundError:
        from nasa_power_client import get_power_data
        from preprocessing import preprocess_power_data

    raw = get_power_data(
        lat=20.9674,
        lon=-89.5926,
        start_date="20250101",
        end_date="20250331",
    )
    df = preprocess_power_data(raw)
    df = calculate_drought_risk(df)
    print(df[["T2M", "PRECTOTCORR", "dry_streak", "drought_risk_score", "risk_category"]].tail(10))
    print("\nResumen actual:")
    print(get_current_risk_summary(df))