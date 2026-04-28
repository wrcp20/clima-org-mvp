import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from app import api_get, get_surveys

st.set_page_config(page_title="Heatmap — Clima Org", layout="wide")
st.title("🗺️ Mapa de Calor por Departamento")

surveys = get_surveys()
if not surveys:
    st.info("No hay campañas disponibles.")
    st.stop()

survey_options = {s["title"]: s["id"] for s in surveys}
selected_title = st.selectbox("Campaña", list(survey_options.keys()))
survey_id = survey_options[selected_title]

dept_data = api_get("/admin/scores/by-department", params={"survey_id": survey_id})

if not dept_data:
    st.info("No hay datos para esta campaña.")
    st.stop()

df = pd.DataFrame(dept_data)

# Normalize scores to 0-1 range for uniform heatmap
dimensions = {
    "Agotamiento": ("avg_exhaustion", 30),
    "Despersonalización": ("avg_depersonalization", 12),
    "Realiz. Personal\n(riesgo)": ("avg_achievement", 12),
    "Clima\n(invertido)": ("avg_climate", 100),
}

z_values = []
for col, (field, max_val) in dimensions.items():
    if field == "avg_climate":
        # Invert climate: higher climate = lower risk
        z_values.append([(100 - row[field]) / 100 for _, row in df.iterrows()])
    else:
        z_values.append([row[field] / max_val for _, row in df.iterrows()])

fig = go.Figure(data=go.Heatmap(
    z=z_values,
    x=df["department"].tolist(),
    y=list(dimensions.keys()),
    colorscale=[
        [0.0, "#27ae60"],   # green = low risk
        [0.5, "#f39c12"],   # yellow = medium
        [1.0, "#e74c3c"],   # red = high risk
    ],
    zmin=0,
    zmax=1,
    text=[[f"{v:.0%}" for v in row] for row in z_values],
    texttemplate="%{text}",
    showscale=True,
    colorbar=dict(title="Nivel de riesgo", tickvals=[0, 0.5, 1], ticktext=["Bajo", "Medio", "Alto"]),
))

fig.update_layout(
    title="Riesgo de burnout por departamento y dimensión",
    xaxis_title="Departamento",
    yaxis_title="Dimensión",
    height=400,
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("El color rojo indica mayor riesgo. Para Clima, se muestra el riesgo inverso (clima bajo = riesgo alto).")
