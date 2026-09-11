"""FastAPI backend: NASA POWER -> modelo de riesgo de sequía -> JSON.

Levantar desde la raíz del proyecto:
    uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

try:  # lanzado desde la raíz del proyecto (uvicorn backend.main:app)
    from backend.drought_risk import compute_risk_series, records, summarize
    from backend.nasa_power_client import get_power_data
    from backend.preprocessing import preprocess_power_data
except ModuleNotFoundError:  # lanzado dentro de backend/ (uvicorn main:app)
    from drought_risk import compute_risk_series, records, summarize
    from nasa_power_client import get_power_data
    from preprocessing import preprocess_power_data

app = FastAPI(
    title="NASA Clima México API",
    description="Demo de hackathon: series climáticas de NASA POWER y "
    "riesgo simplificado de sequía para México.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _power_to_risk(lat: float, lon: float, start_date: str, end_date: str) -> dict:
    """Descarga NASA POWER, preprocesa y calcula el riesgo de sequía."""
    try:
        raw = get_power_data(
            lat, lon, start_date, end_date, parameters=["T2M", "PRECTOTCORR"]
        )
    except Exception as exc:  # noqa: BLE001 - transformar en error HTTPS
        raise HTTPException(status_code=502, detail=f"NASA POWER no respondió: {exc}")

    df = preprocess_power_data(raw)
    if df.empty:
        raise HTTPException(status_code=404, detail="Sin datos para ese punto/periodo")
    return compute_risk_series(df)


@app.get("/health")
def health():
    return {"status": "ok", "api": "NASA Clima México"}


@app.get("/drought-risk")
def drought_risk(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    start_date: str = Query(..., pattern=r"^\d{8}$"),
    end_date: str = Query(..., pattern=r"^\d{8}$"),
):
    """Serie diaria con el score de riesgo y sus componentes."""
    series = _power_to_risk(lat, lon, start_date, end_date)
    return records(series)


@app.get("/drought-risk/summary")
def drought_risk_summary(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    start_date: str = Query(..., pattern=r"^\d{8}$"),
    end_date: str = Query(..., pattern=r"^\d{8}$"),
):
    """Resumen del día más reciente: score, categoría, racha seca y anomalía térmica."""
    series = _power_to_risk(lat, lon, start_date, end_date)
    return summarize(series)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)