import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app import api_get, api_patch

st.set_page_config(page_title="Alertas — Clima Org", layout="wide")
st.title("🚨 Alertas de Riesgo")

show_seen = st.checkbox("Mostrar alertas ya vistas", value=False)
params = {"seen": "false"} if not show_seen else {}

alerts = api_get("/admin/alerts", params=params)

if alerts is None:
    st.stop()

if not alerts:
    st.success("No hay alertas activas. ¡Todo en orden!")
    st.stop()

# Optional department filter
depts = sorted(set(a["department"] for a in alerts))
selected_dept = st.selectbox("Filtrar por departamento", ["Todos"] + depts)
if selected_dept != "Todos":
    alerts = [a for a in alerts if a["department"] == selected_dept]

score_labels = {
    "exhaustion": "Agotamiento",
    "depersonalization": "Despersonalización",
    "achievement": "Realización Personal",
    "climate": "Clima Organizacional",
    "overall": "Riesgo Global",
}

for alert in alerts:
    label = score_labels.get(alert["score_type"], alert["score_type"])
    dept = alert["department"]
    value = alert["value"]
    threshold = alert["threshold"]
    is_seen = alert["seen"]

    if alert["score_type"] == "climate":
        msg = f"**{dept}** — {label}: {value:.1f} (umbral mínimo: {threshold:.0f})"
    else:
        msg = f"**{dept}** — {label}: {value:.1f} (umbral máximo: {threshold:.0f})"

    col1, col2 = st.columns([5, 1])
    with col1:
        if is_seen:
            st.info(f"✓ {msg}")
        elif value >= threshold * 1.2 if alert["score_type"] != "climate" else value <= threshold * 0.8:
            st.error(f"⚠️ {msg}")
        else:
            st.warning(f"⚡ {msg}")
    with col2:
        if not is_seen:
            if st.button("Marcar vista", key=f"seen_{alert['id']}"):
                result = api_patch(f"/admin/alerts/{alert['id']}/seen")
                if result:
                    st.rerun()
