import requests
from datetime import date

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def get_power_data(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
    parameters: list[str] = None,
):
    """Llama a la API de NASA POWER y la regresa el JSON crudo,
    Docs: https://power.larc.nasa.gov/docs/services/api/
    """

    if parameters is None:
        parameters = ["T2M", "PRECTOTCORR"]

    params = {
        "parameters": ",".join(parameters),
        "community": "AG",
        "latitude": lat,
        "longitude": lon,
        "start": start_date,
        "end": end_date,
        "format": "JSON",
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()  # lanza excepcion si falla (4xx, 5xx)

    return response.json()


if __name__ == "__main__":
    # prueba rapida para verificar que la api responde
    data = get_power_data(
        lat=20.9674,
        lon=89.5926,
        start_date="20250101",
        end_date="20250131",
    )
    print(data.keys())
