import pandas as pd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import NASA_BLUE, NASA_GRID, NASA_NAVY, NASA_RED


SEQUENCE = [NASA_BLUE, NASA_RED, "#2E6FD1", "#7EA9E0", "#FF8A70"]


def _style(fig, height=360):
    """Aplica el estilo común a toda gráfica: fondos y gama NASA."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI", size=13, color=NASA_NAVY),
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=NASA_GRID, zeroline=False)
    fig.update_yaxes(gridcolor=NASA_GRID, zeroline=False)
    return fig


def compose_climate(monthly, temp_col="T2M", precip_col="PRECTOTCORR"):
    """Barras de lluvia + línea de temperatura en el mismo eje de tiempo."""
    has_temp = temp_col in monthly.columns
    has_prec = precip_col in monthly.columns

    fig = go.Figure()
    if has_prec:
        fig.add_trace(
            go.Bar(
                x=monthly.index,
                y=monthly[precip_col],
                name="Precipitación (mm)",
                marker_color=NASA_BLUE,
                opacity=0.85,
                yaxis="y2",
            )
        )
    if has_temp:
        fig.add_trace(
            go.Scatter(
                x=monthly.index,
                y=monthly[temp_col],
                name="Temperatura (°C)",
                mode="lines+markers",
                line=dict(color=NASA_RED, width=2.5),
                marker=dict(size=5),
            )
        )
    fig.update_layout(
        title="Temperatura vs. precipitación (mensual)",
        yaxis=dict(
            title="Temperatura (°C)",
            titlefont=dict(color=NASA_RED),
            showgrid=has_temp,
        ),
        yaxis2=dict(
            title="Precipitación (mm)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        showlegend=True,
    )
    if not has_temp:
        fig.update_layout(title="Precipitación mensual (mm)")
    return _style(fig, height=400)


def precipitation_chart(monthly, precip_col):
    """Barras mensuales de lluvia, coloreadas por magnitud."""
    df = monthly.reset_index()
    fig = px.bar(
        df,
        x="fecha",
        y=precip_col,
        color=precip_col,
        color_continuous_scale=[[0, "#FFE4DE"], [1, NASA_BLUE]],
        labels={"fecha": "", precip_col: "Precipitación (mm)"},
    )
    fig.update_layout(title="Precipitación mensual", coloraxis_showscale=False)
    return _style(fig, height=300)


def drought_chart(monthly, spi, precip_col, window=3):
    """Lluvia (barras) + índice SPI (línea) con umbrales de sequía."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly.index,
            y=monthly[precip_col],
            name="Precipitación (mm)",
            marker_color="#BFD0EA",
            opacity=0.9,
            yaxis="y2",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=spi.index,
            y=spi.values,
            name=f"SPI-{window}",
            mode="lines+markers",
            line=dict(color=NASA_RED, width=2.5),
            marker=dict(size=5),
        )
    )
    for level, color, dash in [
        (-0.5, "#C4A62B", "dash"),
        (-0.8, "#E8871E", "dot"),
        (-1.3, "#FC3D21", "dash"),
        (-1.6, "#8E0E2F", "dash"),
    ]:
        fig.add_hline(
            y=level,
            line=dict(color=color, width=1, dash=dash),
            opacity=0.6,
        )
    fig.update_layout(
        title=f"Índice simplificado de sequía (lluvia acumulada a {window} meses)",
        yaxis=dict(title="SPI (z-score)"),
        yaxis2=dict(
            title="Precipitación (mm)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )
    return _style(fig, height=420)


def forecast_chart(observed, forecast, label, color=NASA_RED):
    """Serie observada + pronóstico con banda de incertidumbre."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=observed.index,
            y=observed.values,
            name="Observado",
            mode="lines",
            line=dict(color=NASA_BLUE, width=2),
        )
    )
    if forecast is not None:
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=forecast["alto"],
                mode="lines",
                line=dict(width=0),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=forecast["bajo"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(252,61,33,0.10)",
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast.index,
                y=forecast["valor"],
                name="Pronóstico",
                mode="lines+markers",
                line=dict(color=color, width=2.5, dash="dash"),
            )
        )
    fig.update_layout(title=label)
    return _style(fig, height=320)


def risk_over_time(df, score_col="drought_risk_score"):
    """Serie diaria del score de riesgo que devuelve el backend FastAPI."""
    d = df.reset_index()
    if "date" not in d.columns:
        d = d.rename(columns={d.columns[0]: "date"})
    d["date"] = pd.to_datetime(d["date"])
    fig = px.line(
        d,
        x="date",
        y=score_col,
        labels={"date": "", score_col: "Score de riesgo (0-100)"},
    )
    fig.update_traces(line=dict(color=NASA_RED, width=2.5))
    fig.update_layout(title="Evolución del riesgo de sequía (diario)")
    return _style(fig, height=360)


def climate_daily(df, temp_col="T2M", precip_col="PRECTOTCORR"):
    """Temperatura (línea) + precipitación (barras) diarias desde el backend."""
    d = df.reset_index()
    if "date" not in d.columns:
        d = d.rename(columns={d.columns[0]: "date"})
    d["date"] = pd.to_datetime(d["date"])
    fig = go.Figure()
    if precip_col in d.columns:
        fig.add_trace(
            go.Bar(
                x=d["date"],
                y=d[precip_col],
                name="Precipitación (mm)",
                marker_color=NASA_BLUE,
                opacity=0.85,
                yaxis="y2",
            )
        )
    if temp_col in d.columns:
        fig.add_trace(
            go.Scatter(
                x=d["date"],
                y=d[temp_col],
                name="Temperatura (°C)",
                mode="lines+markers",
                line=dict(color=NASA_RED, width=2.5),
                marker=dict(size=4),
            )
        )
    fig.update_layout(
        title="Temperatura y precipitación (diario)",
        yaxis=dict(title="Temperatura (°C)"),
        yaxis2=dict(
            title="Precipitación (mm)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        showlegend=True,
    )
    return _style(fig, height=360)


def risk_gauge(value, color, category):
    """Medidor 0-100 para el score de riesgo de sequía actual."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"font": {"size": 34, "color": NASA_NAVY}},
            title={"text": f"{category}", "font": {"size": 16, "color": color}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": NASA_NAVY},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 25], "color": "#CBE5D2"},
                    {"range": [25, 50], "color": "#FFE9C2"},
                    {"range": [50, 75], "color": "#FFC4A8"},
                    {"range": [75, 100], "color": "#FCCCC4"},
                ],
                "threshold": {
                    "line": {"color": NASA_NAVY, "width": 3},
                    "value": value,
                    "thickness": 0.9,
                },
            },
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def spi_gauge(value, color):
    """Medidor tipo reloj para el índice de sequía actual."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"font": {"size": 32, "color": NASA_NAVY}},
            gauge={
                "axis": {"range": [-3, 3], "tickwidth": 1, "tickcolor": NASA_NAVY},
                "bar": {"color": color},
                "steps": [
                    {"range": [-3, -1.6], "color": "#8E0E2F"},
                    {"range": [-1.6, -1.3], "color": "#FC3D21"},
                    {"range": [-1.3, -0.8], "color": "#FFC4A8"},
                    {"range": [-0.8, -0.5], "color": "#FFE9C2"},
                    {"range": [-0.5, 3], "color": "#CBE5D2"},
                ],
                "threshold": {
                    "line": {"color": NASA_NAVY, "width": 3},
                    "value": value,
                    "thickness": 0.9,
                },
            },
        )
    )
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig