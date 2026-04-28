import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "change-me")


def api_get(endpoint: str, params: dict = None):
    try:
        resp = requests.get(
            f"{API_URL}{endpoint}",
            headers={"X-Admin-Key": ADMIN_KEY},
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("No se puede conectar a la API. ¿Está corriendo en http://localhost:8000?")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"Error de API: {e.response.status_code} — {e.response.text}")
        return None


def api_patch(endpoint: str, json_data: dict = None):
    try:
        resp = requests.patch(
            f"{API_URL}{endpoint}",
            headers={"X-Admin-Key": ADMIN_KEY},
            json=json_data,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def get_surveys():
    return api_get("/admin/surveys") or []


st.set_page_config(
    page_title="Clima Organizacional",
    page_icon="🏢",
    layout="wide",
)

st.title("Panel de Clima Organizacional")
st.caption("Sistema de análisis de burnout y clima laboral")
