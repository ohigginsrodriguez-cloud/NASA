import pandas as pd
import pydeck as pdk
import streamlit as st


# En 0-255 moviendo el azul oficial de la NASA a RGBA para pydeck
NASA_BLUE_RGBA = [11, 61, 145, 200]


def render_map(lat, lon, label=None):
    """Mapa de ubicación con pydeck centrado en el punto consultado."""
    name = label or f"{lat:.4f}, {lon:.4f}"
    points = pd.DataFrame([{"lat": lat, "lon": lon, "name": name}])

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position="[lon, lat]",
        get_fill_color=NASA_BLUE_RGBA,
        get_radius=60000,
        pickable=True,
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
    )

    view = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=4,
        pitch=0,
        bearing=0,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={"text": "{name}"},
    )
    st.pydeck_chart(deck)