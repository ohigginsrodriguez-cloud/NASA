import os

# --- Backend FastAPI (cuando esté listo) --------------------------------
BASE_URL = os.environ.get("NASA_API_URL", "http://localhost:8000")
USE_BACKEND = os.environ.get("USE_BACKEND", "0") == "1"
REQUEST_TIMEOUT = 60

# --- NASA POWER ----------------------------------------------------------
POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
POWER_COMMUNITY = "AG"  # agroclimatología: clima + agricultura
POWER_MIN_YEAR = 1981   # la serie histórica de POWER arranca en 1981

# --- Paleta basada en el logotipo de la NASA ("meatball") ---------------
# Azul oficial #0B3D91, rojo oficial #FC3D21
NASA_BLUE = "#0B3D91"
NASA_RED = "#FC3D21"
NASA_NAVY = "#10243E"
NASA_SKY = "#2E6FD1"
NASA_LIGHT = "#E8EEF7"
NASA_WHITE = "#FFFFFF"
NASA_GRID = "#DEE5EF"
NASA_TEXT = "#41506B"

# --- Variables disponibles en POWER (diarias) ----------------------------
PARAMS = {
    "T2M": "Temperatura del aire a 2 m (°C)",
    "T2M_MAX": "Temperatura máxima (°C)",
    "T2M_MIN": "Temperatura mínima (°C)",
    "PRECTOTCORR": "Precipitación corregida (mm/día)",
    "RH2M": "Humedad relativa (%)",
    "WS2M": "Velocidad del viento (m/s)",
    "ALLSKY_SFC_SW_DWN": "Radiación solar (kWh/m²/día)",
}
DEFAULT_PARAMS = ["T2M", "PRECTOTCORR"]
TEMP_COL = "T2M"
PRECIP_COL = "PRECTOTCORR"

# --- Ubicaciones de referencia en México ---------------------------------
LOCATIONS = {
    "Ciudad de México": {"lat": 19.4326, "lon": -99.1332},
    "Guadalajara": {"lat": 20.6597, "lon": -103.3496},
    "Monterrey": {"lat": 25.6866, "lon": -100.3161},
    "Hermosillo (árido)": {"lat": 29.0728, "lon": -110.9559},
    "Chihuahua": {"lat": 28.6320, "lon": -106.0691},
    "Mérida": {"lat": 20.9674, "lon": -89.5926},
}
DEFAULT_LOCATION = "Ciudad de México"