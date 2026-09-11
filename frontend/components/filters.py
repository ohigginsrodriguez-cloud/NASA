import streamlit as st


def render_time_range():
    st.markdown("###  Rango de fechas")
    start = st.date_input("Desde", value=None)
    end = st.date_input("Hasta", value=None)
    return start, end


def render_coordinates():
    st.markdown("###  Coordenadas")
    lat = st.number_input("Latitud", min_value=-90.0, max_value=90.0, value=0.0, step=0.1)
    lon = st.number_input("Longitud", min_value=-180.0, max_value=180.0, value=0.0, step=0.1)
    return lat, lon


def render_sliders():
    st.markdown("###  Parámetros")
    pa = st.slider("Parámetro A", 0, 100, 50)
    pb = st.slider("Parámetro B", 0.0, 10.0, 1.0, step=0.1)
    return pa, pb


def render_filters():
    with st.sidebar:
        st.markdown("##  NASA Hackathon")
        st.markdown("---")
        start, end = render_time_range()
        lat, lon = render_coordinates()
        pa, pb = render_sliders()
        st.markdown("---")
        aplicar = st.button("Aplicar filtros")
    return {"start": start, "end": end, "lat": lat, "lon": lon, "pa": pa, "pb": pb, "aplicar": aplicar}