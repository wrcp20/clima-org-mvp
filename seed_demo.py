"""
Seed script: crea datos demo para explorar el dashboard.
Uso: python seed_demo.py [--api-url http://localhost:8000] [--key TU_API_KEY]
"""
import argparse
import random
import sys
import time

import requests

parser = argparse.ArgumentParser()
parser.add_argument("--api-url", default="http://localhost:8000")
parser.add_argument("--key", default="change-me")
args = parser.parse_args()

BASE = args.api_url
HEADERS = {"X-Admin-Key": args.key, "Content-Type": "application/json"}

DEPARTMENTS = ["Engineering", "Marketing", "Ventas", "RRHH", "Operaciones"]

# Perfiles de respuesta por departamento (simula distintos niveles de burnout)
PROFILES = {
    "Engineering":  {"mbi": 4, "climate": 2},   # alto burnout, bajo clima
    "Marketing":    {"mbi": 2, "climate": 4},   # bajo burnout, buen clima
    "Ventas":       {"mbi": 5, "climate": 2},   # burnout muy alto
    "RRHH":         {"mbi": 1, "climate": 5},   # saludable
    "Operaciones":  {"mbi": 3, "climate": 3},   # medio
}

def check_api():
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        r.raise_for_status()
        print(f"✓ API disponible en {BASE}")
    except Exception as e:
        print(f"✗ No se puede conectar a {BASE}: {e}")
        print("  Asegurate de que la API esté corriendo: docker compose up")
        sys.exit(1)

def create_survey(title: str, date: str) -> dict:
    r = requests.post(f"{BASE}/admin/surveys", headers=HEADERS,
                      json={"title": title, "campaign_date": date})
    r.raise_for_status()
    return r.json()

def activate_survey(survey_id: str):
    r = requests.patch(f"{BASE}/admin/surveys/{survey_id}/status", headers=HEADERS,
                       json={"status": "active"})
    r.raise_for_status()

def generate_tokens(survey_id: str, department: str, count: int) -> list[str]:
    r = requests.post(f"{BASE}/admin/surveys/{survey_id}/tokens", headers=HEADERS,
                      json={"department": department, "count": count})
    r.raise_for_status()
    return r.json()["tokens"]

def make_answers(mbi_level: int, climate_level: int) -> dict:
    """Genera respuestas con variación aleatoria alrededor del nivel base."""
    def clamp(v, lo, hi): return max(lo, min(hi, v))
    answers = {}
    for i in range(1, 23):   # q1-q22: escala 0-6 (MBI)
        noise = random.randint(-1, 1)
        answers[f"q{i}"] = clamp(mbi_level + noise, 0, 6)
    for i in range(23, 29):  # q23-q28: escala 1-5 (clima)
        noise = random.randint(-1, 1)
        answers[f"q{i}"] = clamp(climate_level + noise, 1, 5)
    return answers

def submit_response(survey_id: str, token: str, answers: dict) -> dict:
    r = requests.post(
        f"{BASE}/surveys/{survey_id}/respond",
        params={"token": token},
        json={"answers": answers},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()

def seed_campaign(title: str, date: str, employees_per_dept: int = 5):
    print(f"\n📋 Creando campaña: {title}")
    survey = create_survey(title, date)
    survey_id = survey["id"]
    print(f"   ID: {survey_id}")

    activate_survey(survey_id)
    print("   Estado: activo")

    total = 0
    for dept in DEPARTMENTS:
        profile = PROFILES[dept]
        tokens = generate_tokens(survey_id, dept, employees_per_dept)
        scores_summary = []
        for token in tokens:
            answers = make_answers(profile["mbi"], profile["climate"])
            result = submit_response(survey_id, token, answers)
            scores_summary.append(result["risk_level"])
            total += 1

        risk_counts = {r: scores_summary.count(r) for r in ["low", "medium", "high"]}
        print(f"   {dept:15} → {employees_per_dept} respuestas | "
              f"🟢{risk_counts['low']} 🟡{risk_counts['medium']} 🔴{risk_counts['high']}")

    print(f"   Total respuestas: {total}")
    return survey_id

if __name__ == "__main__":
    print("=" * 55)
    print("  Clima Org MVP — Seed de datos demo")
    print("=" * 55)

    check_api()

    # Campaña 1 — hace 3 meses
    seed_campaign("Q1 2026", "2026-01-15", employees_per_dept=6)

    # Campaña 2 — reciente
    seed_campaign("Q2 2026", "2026-04-01", employees_per_dept=6)

    print("\n✅ Datos cargados. Abrí el dashboard:")
    print(f"   http://localhost:8501")
    print("\n   Swagger API docs:")
    print(f"   {BASE}/docs")
