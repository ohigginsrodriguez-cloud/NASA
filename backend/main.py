from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from nasa_power_client import get_power_data
from preprocessing import preprocess_power_data
from predict import calculate_drought_risk, get_current_risk_summary

app = FastAPI(title="Drought Risk API - NASA Space Apps Practice")

# CORS: necesario para que Streamlit (u otro origen) pueda llamar a este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # para práctica está bien abierto; en prod se restringe
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Drought Risk API funcionando"}


@app.get("/drought-risk")
def drought_risk(
    lat: float,
    lon: float,
    start_date: str,  # formato YYYYMMDD
    end_date: str,  # formato YYYYMMDD
):
    """
    Regresa la serie histórica completa con score de riesgo de sequía por día.
    """
    try:
        raw = get_power_data(lat, lon, start_date, end_date)
        df = preprocess_power_data(raw)
        df = calculate_drought_risk(df)
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Error consultando NASA POWER: {e}"
        )

    # convertir a formato JSON-friendly (lista de registros con fecha como string)
    df_reset = df.reset_index()
    df_reset["date"] = df_reset["date"].dt.strftime("%Y-%m-%d")

    return df_reset.to_dict(orient="records")


@app.get("/drought-risk/summary")
def drought_risk_summary(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
):
    """
    Regresa solo el resumen del día más reciente (más liviano para un dashboard simple).
    """
    try:
        raw = get_power_data(lat, lon, start_date, end_date)
        df = preprocess_power_data(raw)
        df = calculate_drought_risk(df)
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Error consultando NASA POWER: {e}"
        )

    return get_current_risk_summary(df)
