import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
from app import api_get, get_surveys

st.set_page_config(page_title="Overview — Clima Org", layout="wide")
st.title("📊 Overview General")

surveys = get_surveys()
if not surveys:
    st.info("No hay campañas disponibles. Creá una desde la API admin.")
    st.stop()

survey_options = {s["title"]: s["id"] for s in surveys}
selected_title = st.selectbox("Seleccionar campaña", list(survey_options.keys()))
survey_id = survey_options[selected_title]

dept_data = api_get("/admin/scores/by-department", params={"survey_id": survey_id})
response_summary = api_get("/admin/responses/summary", params={"survey_id": survey_id})

if not dept_data:
    st.info("No hay datos de scores para esta campaña todavía.")
    st.stop()

df = pd.DataFrame(dept_data)

# KPIs
total_responses = sum(r["response_count"] for r in (response_summary or []))
avg_climate = df["avg_climate"].mean() if not df.empty else 0
high_risk_count = len(df[df["dominant_risk"] == "high"]) if not df.empty else 0
total_depts = len(df)
pct_high_risk = (high_risk_count / total_depts * 100) if total_depts > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total respuestas", total_responses)
col2.metric("Clima promedio", f"{avg_climate:.1f} / 100")
col3.metric("Departamentos en riesgo alto", f"{high_risk_count} ({pct_high_risk:.0f}%)")

st.markdown("---")
st.subheader("Resumen por departamento")

risk_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
df["riesgo"] = df["dominant_risk"].map(risk_colors)
df_display = df[["riesgo", "department", "avg_exhaustion", "avg_depersonalization", "avg_achievement", "avg_climate", "count"]].copy()
df_display.columns = ["", "Departamento", "Agotamiento", "Desp.", "Realización", "Clima", "Respuestas"]
st.dataframe(df_display, use_container_width=True, hide_index=True)
