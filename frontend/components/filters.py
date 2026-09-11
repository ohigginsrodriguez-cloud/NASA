import datetime as dt

import streamlit as st

from config import (
    DEFAULT_LOCATION,
    DEFAULT_PARAMS,
    LOCATIONS,
    PARAMS,
    POWER_MIN_YEAR,
)


def render_filters():
    """Sidebar: presets de ubicaciÃ³n, coordenadas, periodo y variables."""
    with st.sidebar:
        st.markdown("### Panel de consulta")
        st.caption("Variables fÃ­sicas satelitales de NASA POWER.")

        preset = st.selectbox(
            "UbicaciÃ³n",
            list(LOCATIONS),
            index=list(LOCATIONS.keys()).index(DEFAULT_LOCATION),
        )
        lat, lon = LOCATIONS[preset]["lat"], LOCATIONS[preset]["lon"]

        c1, c2 = st.columns(2)
        lat = c1.number_input("Latitud", -90.0, 90.0, lat, step=0.0001, format="%.4f")
        lon = c2.number_input("Longitud", -180.0, 180.0, lon, step=0.0001, format="%.4f")

        st.markdown("**Periodo**")
        today = dt.date.today()
        default_start = today.replace(year=today.year - 6)
        rango = st.date_input(
            "Rango de fechas",
            value=(default_start, today),
            min_value=dt.date(POWER_MIN_YEAR, 1, 1),
            max_value=today,
        )
        if isinstance(rango, (tuple, list)) and len(rango) == 2:
            start, end = rango
        else:
            start, end = default_start, today

        if start >= end:
            st.error("La fecha inicial debe ser anterior a la final.")
            start, end = default_start, today

        params = st.multiselect("Variables", list(PARAMS), default=DEFAULT_PARAMS)
        if not params:
            st.warning("Selecciona al menos una variable.")
            params = DEFAULT_PARAMS[:1]

        st.markdown("---")
        aplicar = st.button("Cargar datos", type="primary", width="stretch")

    return {
        "lat": lat,
        "lon": lon,
        "start": start,
        "end": end,
        "params": params,
        "aplicar": aplicar,
    }