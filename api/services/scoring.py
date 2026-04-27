from constants import SURVEY_QUESTIONS


EXHAUSTION_THRESHOLD = 20
DEPERSONALIZATION_THRESHOLD = 8
ACHIEVEMENT_THRESHOLD = 8


def calculate_scores(answers: dict[str, int]) -> dict:
    exhaustion = sum(answers[f"q{i}"] for i in range(1, 6))
    depersonalization = sum(answers[f"q{i}"] for i in range(6, 8))
    achievement = sum(6 - answers[f"q{i}"] for i in range(8, 10))

    climate_raw = sum(answers[f"q{i}"] for i in range(10, 16)) / 6
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
