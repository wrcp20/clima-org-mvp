import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.express as px
import streamlit as st
from app import api_get, get_surveys

st.set_page_config(page_title="Tendencias — Clima Org", layout="wide")
st.title("📈 Tendencias por Campaña")

surveys = get_surveys()
if not surveys or len(surveys) < 2:
    st.info("Se necesitan al menos 2 campañas para ver tendencias.")
    if surveys:
        st.caption(f"Campaña actual: {surveys[0]['title']}")
    st.stop()

# Multi-select surveys
selected_titles = st.multiselect(
    "Seleccionar campañas a comparar",
    [s["title"] for s in surveys],
    default=[s["title"] for s in surveys[:2]],
)

if not selected_titles:
    st.warning("Seleccioná al menos una campaña.")
    st.stop()

selected_surveys = [s for s in surveys if s["title"] in selected_titles]

# Collect data for all selected surveys
all_data = []
for survey in selected_surveys:
    dept_data = api_get("/admin/scores/by-department", params={"survey_id": survey["id"]})
    if dept_data:
        for row in dept_data:
            row["campaign"] = survey["title"]
            row["campaign_date"] = survey.get("campaign_date", survey["title"])
            all_data.append(row)

if not all_data:
    st.info("No hay datos para las campañas seleccionadas.")
    st.stop()

df = pd.DataFrame(all_data)

# Department filter
all_depts = sorted(df["department"].unique())
selected_depts = st.multiselect("Departamentos", all_depts, default=all_depts)
if selected_depts:
    df = df[df["department"].isin(selected_depts)]

metric = st.selectbox(
    "Métrica a visualizar",
    ["avg_exhaustion", "avg_depersonalization", "avg_achievement", "avg_climate"],
    format_func=lambda x: {
        "avg_exhaustion": "Agotamiento (0-30)",
        "avg_depersonalization": "Despersonalización (0-12)",
        "avg_achievement": "Realización personal (0-12)",
        "avg_climate": "Clima (0-100)",
    }[x],
)

fig = px.line(
    df,
    x="campaign",
    y=metric,
    color="department",
    markers=True,
    title=f"Evolución de {metric} por campaña",
    labels={"campaign": "Campaña", metric: "Score promedio", "department": "Departamento"},
)
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)
