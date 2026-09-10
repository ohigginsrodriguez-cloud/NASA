import requests
import streamlit as st

from frontend.config import BASE_URL, REQUEST_TIMEOUT


@st.cache_data(ttl=300, show_spinner=False)
def get(endpoint, params=None):
    response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60, show_spinner=False)
def post(endpoint, payload=None):
    response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()