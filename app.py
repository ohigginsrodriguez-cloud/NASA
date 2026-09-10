import streamlit as st

st.set_page_config(
    page_title="NASA Hackathon",
    page_icon="🚀",
    layout="centered",
)

st.title("🚀 NASA Hackathon")
st.subheader("App base para el proyecto")

st.write(
    "Este es el frontend base de Streamlit. "
    "Aquí puedes agregar tu visualización de datos, imágenes o análisis."
)

tab1, tab2 = st.tabs(["Intro", "Datos"])

with tab1:
    st.markdown(
        """
        ### ¿Por dónde empezar?
        - Usa `requests` para consumir APIs de la NASA.
        - API abiertas: **APOD**, **Mars Rover Photos**, **CEMS**, **NEO**.
        - Agrega gráficos con `plotly` o `matplotlib`.
        """
    )

with tab2:
    numero = st.number_input("Número de ejemplo", min_value=1, max_value=100, value=10)
    st.write(f"Cuadrado del valor: {numero ** 2}")
    st.progress(numero / 100)

if st.button("Lanzar pasos de misión"):
    for i in range(1, 6):
        st.write(f"Paso {i} completado")
        st.progress(i / 5)