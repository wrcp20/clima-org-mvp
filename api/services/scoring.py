from constants import SURVEY_QUESTIONS

# MBI-HSS validated high-burnout cutoffs
# Exhaustion:       9 items × 6 = 54 max  → high ≥ 27
# Depersonalization: 5 items × 6 = 30 max  → high ≥ 13
# Achievement:       8 items × 6 = 48 max (inverted) → high ≥ 17  (original PA ≤ 31)
EXHAUSTION_THRESHOLD = 27
DEPERSONALIZATION_THRESHOLD = 13
ACHIEVEMENT_THRESHOLD = 17


def calculate_scores(answers: dict[str, int]) -> dict:
    exhaustion = sum(answers[f"q{i}"] for i in range(1, 10))        # q1-q9
    depersonalization = sum(answers[f"q{i}"] for i in range(10, 15)) # q10-q14
    achievement = sum(6 - answers[f"q{i}"] for i in range(15, 23))  # q15-q22, inverted

    climate_raw = sum(answers[f"q{i}"] for i in range(23, 29)) / 6  # q23-q28, avg 1-5
    climate_score = round((climate_raw - 1) / 4 * 100, 1)

    high_dims = sum([
        exhaustion >= EXHAUSTION_THRESHOLD,
        depersonalization >= DEPERSONALIZATION_THRESHOLD,
        achievement >= ACHIEVEMENT_THRESHOLD,
    ])
    risk_level = "high" if high_dims >= 2 else "medium" if high_dims == 1 else "low"

    return {
        "exhaustion_score": exhaustion,
        "depersonalization_score": depersonalization,
        "personal_achievement_score": achievement,
        "climate_score": climate_score,
        "risk_level": risk_level,
    }
