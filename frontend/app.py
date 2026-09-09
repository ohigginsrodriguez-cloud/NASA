import pandas as pd
import streamlit as st

from frontend.components.charts import bar_chart, line_chart
from frontend.components.filters import render_filters
from frontend.components.map_view import render_map


def build_layout(filtros):
    st.set_page_config(page_title="NASA Hackathon", page_icon="🚀", layout="wide")

    st.markdown("## 🚀 NASA Hackathon")
    st.markdown("### Dashboard")
    st.markdown("---")

    if filtros["aplicar"]:
        st.success("Filtros aplicados (integra con tu backend FastAPI).")
        st.write("Parámetros:", filtros)

    col_data, col_map = st.columns(2)

    df = pd.DataFrame(
        {
            "fecha": pd.date_range("2025-01-01", periods=10, freq="D"),
            "valor": [12, 18, 9, 22, 15, 27, 31, 24, 19, 28],
            "lat": [19.4, 20.1, 19.9, 20.5, 18.9, 19.2, 21.2, 20.0, 19.6, 20.8],
            "lon": [-99.1, -98.8, -99.3, -99.5, -98.9, -99.0, -98.7, -99.2, -99.4, -98.6],
        }
    )

    with col_data:
        line_chart(df, "fecha", "valor")
        bar_chart(df, "fecha", "valor")

    with col_map:
        st.markdown("### Mapa")
        render_map(df, lat=20.0, lon=-99.0)


def main():
    filtros = render_filters()
    build_layout(filtros)


if __name__ == "__main__":
    main()