import pandas as pd
import pydeck as pdk
import streamlit as st

NASA_LAYER_COLOR = [11, 61, 145, 180]


def render_map(df=None, lat=0.0, lon=0.0):
    points = df if df is not None else pd.DataFrame([{"lat": lat, "lon": lon}])

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position=["lon", "lat"],
        get_fill_color=NASA_LAYER_COLOR,
        get_radius=50000,
        pickable=True,
    )

    view = pdk.ViewState(latitude=lat, longitude=lon, zoom=2)

    deck = pdk.Deck(layers=[layer], initial_view_state=view, tooltip={"text": "{lat}, {lon}"})

    st.pydeck_chart(deck)