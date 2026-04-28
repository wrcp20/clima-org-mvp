import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import requests
import pandas as pd
import streamlit as st
from app import get_surveys, API_URL, ADMIN_KEY

st.set_page_config(page_title="Exportar — Clima Org", layout="wide")
st.title("📥 Exportar Datos")

surveys = get_surveys()
if not surveys:
    st.info("No hay campañas disponibles.")
    st.stop()

survey_options = {s["title"]: s["id"] for s in surveys}
selected_title = st.selectbox("Campaña a exportar", list(survey_options.keys()))
survey_id = survey_options[selected_title]

# Fetch CSV data
try:
    resp = requests.get(
        f"{API_URL}/admin/scores/export",
        headers={"X-Admin-Key": ADMIN_KEY},
        params={"survey_id": survey_id},
        timeout=10,
    )
    resp.raise_for_status()
    csv_content = resp.content
    csv_text = resp.content.decode("utf-8")
except Exception as e:
    st.error(f"Error al obtener datos: {e}")
    st.stop()

# Preview
st.subheader("Vista previa (primeros 10 registros)")
try:
    df = pd.read_csv(io.StringIO(csv_text))
    if df.empty:
        st.info("No hay scores para esta campaña todavía.")
    else:
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
        st.caption(f"Total de registros: {len(df)}")
except Exception:
    st.warning("No se pudo generar la vista previa.")

st.markdown("---")

# Download button
st.download_button(
    label="Descargar CSV completo",
    data=csv_content,
    file_name=f"scores_{selected_title.replace(' ', '_')}.csv",
    mime="text/csv",
)
