import pandas as pd


def calculate_drought_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula un score de riesgo de sequía por día, basado en:
    - días consecutivos sin lluvia significativa
    - temperatura por encima del promedio del periodo

    Regresa el DataFrame original + columnas nuevas de riesgo.
    """
    df = df.copy()

    # 1. Marcar días "secos" (menos de 1mm de lluvia se considera insignificante)
    df["is_dry_day"] = df["PRECTOTCORR"] < 1.0

    # 2. Contar racha de días secos consecutivos
    df["dry_streak"] = df["is_dry_day"].groupby((~df["is_dry_day"]).cumsum()).cumsum()

    # 3. Temperatura relativa al promedio del periodo
    avg_temp = df["T2M"].mean()
    df["temp_anomaly"] = df["T2M"] - avg_temp

    # 4. Score simple combinando ambos factores (0 a 100)
    # normalizamos dry_streak (tope en 30 días) y temp_anomaly (tope en 5°C)
    dry_score = (df["dry_streak"].clip(upper=30) / 30) * 60  # peso 60%
    temp_score = (df["temp_anomaly"].clip(lower=0, upper=5) / 5) * 40  # peso 40%

    df["drought_risk_score"] = (dry_score + temp_score).round(1)

    # 5. Categoría legible para la demo
    df["risk_category"] = pd.cut(
        df["drought_risk_score"],
        bins=[-1, 25, 50, 75, 100],
        labels=["Bajo", "Moderado", "Alto", "Crítico"],
    )

    return df


def get_current_risk_summary(df: pd.DataFrame) -> dict:
    """
    Regresa un resumen del riesgo más reciente, útil para el endpoint
    que consume el frontend (no necesitas mandar toda la serie histórica
    si solo quieres mostrar el estado actual).
    """
    latest = df.iloc[-1]
    return {
        "date": latest.name.strftime("%Y-%m-%d"),
        "drought_risk_score": float(latest["drought_risk_score"]),
        "risk_category": str(latest["risk_category"]),
        "dry_streak_days": int(latest["dry_streak"]),
        "temp_anomaly_c": round(float(latest["temp_anomaly"]), 1),
    }


if __name__ == "__main__":
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

    print(
        df[
            ["T2M", "PRECTOTCORR", "dry_streak", "drought_risk_score", "risk_category"]
        ].tail(10)
    )
    print("\nResumen actual:")
    print(get_current_risk_summary(df))
