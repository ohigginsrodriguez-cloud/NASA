import pandas as pd
import plotly.express as px
import streamlit as st

NASA_COLORS = ["#0B3D91", "#FC3D21", "#1E90FF", "#FFD700"]


def line_chart(df, x, y):
    fig = px.line(df, x=x, y=y, color_discrete_sequence=NASA_COLORS)
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(df, x, y=None):
    fig = px.bar(df, x=x, y=y, color_discrete_sequence=NASA_COLORS)
    st.plotly_chart(fig, use_container_width=True)


def scatter_geo(df, lat_col, lon_col, color=None):
    fig = px.scatter_geo(
        df,
        lat=lat_col,
        lon=lon_col,
        color=color,
        color_discrete_sequence=NASA_COLORS,
        projection="natural earth",
    )
    st.plotly_chart(fig, use_container_width=True)