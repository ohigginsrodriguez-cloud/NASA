"""NASA Clima MÃ©xico â€” interfaz Streamlit (demo de hackathon).

Flujo de datos: frontend -> API FastAPI (/drought-risk) -> NASA POWER.
"""

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu

from api_client import drought_risk_records, drought_risk_summary
from components.charts import climate_daily, risk_gauge, risk_over_time
from components.filters import render_filters
from components.map_view import render_map
from config import (
    NASA_BLUE,
    NASA_GRID,
    NASA_LIGHT,
    NASA_NAVY,
    NASA_RED,
    NASA_SKY,
    NASA_TEXT,
    NASA_WHITE,
)

RISK_COLORS = {
    "Bajo": "#2E7D32",
    "Moderado": "#E8871E",
    "Alto": "#FC3D21",
    "CrÃ­tico": "#8E0E2F",
}

st.set_page_config(
    page_title="NASA Clima MÃ©xico",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css():
    st.markdown(
        f"""
        <style>
          html, body, [class*="css"] {{ font-family: 'Segoe UI', 'Helvetica Neue', sans-serif; }}
          .stApp {{ background: #F7F9FC; }}
          header[data-testid="stHeader"] {{ background: transparent; }}
          #MainMenu, footer {{ visibility: hidden; }}

          [data-testid="stSidebar"] {{ background: {NASA_LIGHT}; }}
          [data-testid="stSidebar"] h3 {{ color: {NASA_BLUE}; font-weight: 700; }}
          [data-testid="stSidebar"] .stCaption {{ color: {NASA_TEXT}; }}

          [data-testid="stMetric"] {{
            background: {NASA_WHITE};
            border: 1px solid {NASA_GRID};
            border-radius: 12px;
            padding: 10px 14px;
            box-shadow: 0 1px 3px rgba(16,36,62,.06);
          }}
          [data-testid="stMetricValue"] {{ color: {NASA_NAVY}; }}

          .hero {{
            display: flex; align-items: center; gap: 16px;
            background: linear-gradient(120deg, {NASA_BLUE} 0%, #1755C4 55%, {NASA_BLUE} 100%);
            border-bottom: 4px solid {NASA_RED};
            border-radius: 14px; padding: 20px 24px;
            box-shadow: 0 4px 14px rgba(11,61,145,.18);
            margin-bottom: 6px;
          }}
          .hero-badge {{
            width: 46px; height: 46px; border-radius: 50%; flex-shrink: 0;
            background: {NASA_BLUE}; color: {NASA_WHITE};
            display: flex; align-items: center; justify-content: center;
            font-weight: 800; font-size: 21px;
            border: 3px solid {NASA_RED};
            box-shadow: 0 2px 6px rgba(11,61,145,.4);
          }}
          .hero-title {{ color: {NASA_WHITE}; font-size: 25px; font-weight: 800; letter-spacing: 2px; }}
          .hero-sub {{ color: #BFD0EA; font-size: 13.5px; margin-top: 2px; }}
          .meta {{ color: {NASA_TEXT}; font-size: 12.5px; margin-top: 2px; margin-bottom: 10px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(lat, lon, periodo):
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-badge">N</div>
          <div>
            <div class="hero-title">NASA <span style="color:#9FC1FF;">Â·</span> CLIMA MÃ‰XICO</div>
            <div class="hero-sub">Riesgo de sequÃ­a en MÃ©xico a partir de datos satelitales</div>
          </div>
        </div>
        <div class="meta">
          Punto: {lat:.4f}&deg;, {lon:.4f}&deg; &nbsp;&middot;&nbsp; Periodo: {periodo}
          &nbsp;&middot;&nbsp; Flujo: Streamlit â†’ FastAPI â†’ NASA POWER
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_from_backend(filtros):
    """Pide las series y el resumen al backend FastAPI."""
    try:
        with st.spinner("Consultando el backend y descargando NASA POWERâ€¦"):
            df = drought_risk_records(filtros["lat"], filtros["lon"], filtros["start"], filtros["end"])
            summary = drought_risk_summary(filtros["lat"], filtros["lon"], filtros["start"], filtros["end"])
        return df, summary
    except Exception as exc:  # noqa: BLE001 - mensaje claro para el usuario
        st.error("No se pudo conectar con el backend FastAPI.")
        st.caption(
            f"Detalle: {exc}\n\nPara levantarlo: "
            "`uvicorn backend.main:app --reload --port 8000` (desde la raÃ­z del proyecto)."
        )
        return None, None


def render_kpis(df, summary):
    category = summary["risk_category"]
    color = RISK_COLORS.get(category, NASA_TEXT)

    lluvia_total = float(df["PRECTOTCORR"].sum())
    temp_media = float(df["T2M"].mean())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Score de riesgo", f"{summary['drought_risk_score']:.0f}", "/ 100")
    k2.metric("CategorÃ­a", category, "")
    k3.metric("DÃ­as secos consecutivos", summary["dry_streak_days"], "dÃ­as")
    k4.metric("PrecipitaciÃ³n total", f"{lluvia_total:.0f}", "mm")

    style_metric_cards(
        background_color=NASA_WHITE,
        border_color=NASA_GRID,
        border_radius_px=12,
        border_left_color=[NASA_BLUE, color, NASA_RED, NASA_SKY],
        box_shadow=False,
    )


def render_riesgo_tab(df, summary):
    category = summary["risk_category"]
    color = RISK_COLORS.get(category, NASA_TEXT)

    col_g, col_c = st.columns([1, 2])
    with col_g:
        st.plotly_chart(risk_gauge(summary["drought_risk_score"], color, category), width="stretch")
    with col_c:
        st.markdown("**Â¿CÃ³mo se calcula el riesgo?**")
        st.caption(
            "Un score de 0 a 100 que combina tres seÃ±ales diarias de NASA POWER: "
            "dÃ©ficit de lluvia frente a la climatologÃ­a reciente (45%), racha de dÃ­as "
            "secos consecutivos (30%) y anomalÃ­a de temperatura (25%). La categorÃ­a "
            "sigue umbrales sencillos (Bajo/Moderado/Alto/CrÃ­tico). Es un modelo "
            "didÃ¡ctico, no el monitoreo oficial de CONAGUA."
        )
        st.plotly_chart(risk_over_time(df), width="stretch")


def render_clima_tab(df):
    st.plotly_chart(climate_daily(df), width="stretch")

    with st.expander("Ver serie histÃ³rica"):
        table = df.reset_index()
        table["date"] = table["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(
            table[
                [
                    "date",
                    "T2M",
                    "PRECTOTCORR",
                    "dry_streak",
                    "temp_anomaly",
                    "drought_risk_score",
                    "risk_category",
                ]
            ],
            width="stretch",
            hide_index=True,
        )


def render_ubicacion_tab(lat, lon):
    render_map(lat, lon)


def main():
    inject_css()
    filtros = render_filters()

    render_header(filtros["lat"], filtros["lon"], f"{filtros['start']} â†’ {filtros['end']}")

    if not filtros["aplicar"]:
        st.info(
            "Ajusta la ubicaciÃ³n, el periodo y las variables en la barra lateral "
            "y presiona **Cargar datos**."
        )
        return

    df, summary = load_from_backend(filtros)
    if df is None or df.empty:
        return

    render_kpis(df, summary)
    st.markdown("")

    tab = option_menu(
        None,
        ["Riesgo", "Clima", "UbicaciÃ³n"],
        icons=["droplet-half", "thermometer-half", "geo-alt-fill"],
        menu_icon=None,
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": NASA_BLUE, "font-size": "15px"},
            "nav-link": {"font-size": "14px", "color": NASA_TEXT, "--hover-color": NASA_LIGHT},
            "nav-link-selected": {"background-color": NASA_BLUE, "color": NASA_WHITE},
        },
    )

    if tab == "Riesgo":
        render_riesgo_tab(df, summary)
    elif tab == "Clima":
        render_clima_tab(df)
    else:
        render_ubicacion_tab(filtros["lat"], filtros["lon"])

    st.caption(
        "Demo para hackathon Â· Datos: NASA POWER (Prediction Of Worldwide Energy Resources) Â· "
        "El Ã­ndice de riesgo es una simplificaciÃ³n didÃ¡ctica y no sustituye el monitoreo oficial."
    )


if __name__ == "__main__":
    main()