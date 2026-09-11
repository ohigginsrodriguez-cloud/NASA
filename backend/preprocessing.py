import pandas as pd

MISSING_VALUE = -999.0  # NASA POWER usa esto para datos faltantes


def power_json_to_dataframe(raw_json: dict) -> pd.DataFrame:
    """
    Convierte el JSON crudo de NASA POWER en un DataFrame con:
    columnas = parametros (T2M, PRECTOTOCORR, ...)
    indice = fecha (datetime)
    """
    parameter_data = raw_json["properties"]["parameter"]
    # parameter_data = {"T2M": {"20250101": 24.3, "20250102": 25.1, ...}, "PRECTOTCORR": {...}}

    df = pd.DataFrame(parameter_data)
    # el indice queda como string "20250101", lo convertimos a datetime real
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"

    return df


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remplaza el valor -999 (missing) por NaN, y luego interpola
    para no dejar huecos en los datos
    """

    df = df.replace(MISSING_VALUE, pd.NA)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.interpolate(method="linear").ffill().bfill()
    return df


def preprocess_power_data(raw_json: dict) -> pd.DataFrame:
    """
    Pipeline completo: JSON crudo -> DataFrame limpio y listo para usar
    """

    df = power_json_to_dataframe(raw_json)
    df = clean_missing_values(df)
    return df


if __name__ == "__main__":
    from nasa_power_client import get_power_data

    raw = get_power_data(
        lat=20.9674,
        lon=-89.5926,
        start_date="20250101",
        end_date="20250131",
    )
    df = preprocess_power_data(raw)
    print(df.head())
    print(df.info())
