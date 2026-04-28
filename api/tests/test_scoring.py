from services.scoring import (
    calculate_scores,
    EXHAUSTION_THRESHOLD,
    DEPERSONALIZATION_THRESHOLD,
)


def _answers(mbi_val: int = 0, climate_val: int = 1) -> dict[str, int]:
    answers = {f"q{i}": mbi_val for i in range(1, 23)}
    answers.update({f"q{i}": climate_val for i in range(23, 29)})
    return answers


def test_all_zeros_mbi_min_climate():
    result = calculate_scores(_answers(mbi_val=0, climate_val=1))
    assert result["exhaustion_score"] == 0
    assert result["depersonalization_score"] == 0
    assert result["personal_achievement_score"] == 48  # 8 items × (6-0) = 48
    assert result["climate_score"] == 0.0
    assert result["risk_level"] == "medium"  # only achievement at risk (1 dim)


def test_all_max_values():
    result = calculate_scores(_answers(mbi_val=6, climate_val=5))
    assert result["exhaustion_score"] == 54    # 9 × 6
    assert result["depersonalization_score"] == 30  # 5 × 6
    assert result["personal_achievement_score"] == 0   # 6-6=0 × 8
    assert result["climate_score"] == 100.0
    assert result["risk_level"] == "high"  # exhaustion + depersonalization


def test_exhaustion_threshold():
    answers = _answers(mbi_val=0, climate_val=3)
    for i in range(1, 10):
        answers[f"q{i}"] = 3  # 9×3=27 = threshold
    for i in range(15, 23):
        answers[f"q{i}"] = 6  # achievement inverted = 0 (not at risk)
    result = calculate_scores(answers)
    assert result["exhaustion_score"] == EXHAUSTION_THRESHOLD
    assert result["risk_level"] == "medium"  # only exhaustion at risk


def test_depersonalization_threshold():
    answers = _answers(mbi_val=0, climate_val=3)
    for i in range(10, 15):
        answers[f"q{i}"] = 3  # 5×3=15 > 13 threshold
    for i in range(15, 23):
        answers[f"q{i}"] = 6  # achievement inverted = 0
    result = calculate_scores(answers)
    assert result["depersonalization_score"] >= DEPERSONALIZATION_THRESHOLD
    assert result["risk_level"] == "medium"  # only depersonalization at risk


def test_two_dimensions_high_is_high_risk():
    answers = _answers(mbi_val=0, climate_val=3)
    for i in range(1, 10):
        answers[f"q{i}"] = 3   # exhaustion = 27
    for i in range(10, 15):
        answers[f"q{i}"] = 3   # depersonalization = 15
    for i in range(15, 23):
        answers[f"q{i}"] = 6   # achievement inverted = 0
    result = calculate_scores(answers)
    assert result["risk_level"] == "high"


def test_climate_score_maximum():
    result = calculate_scores(_answers(mbi_val=0, climate_val=5))
    assert result["climate_score"] == 100.0


def test_climate_score_minimum():
    result = calculate_scores(_answers(mbi_val=0, climate_val=1))
    assert result["climate_score"] == 0.0


def test_climate_score_midpoint():
    result = calculate_scores(_answers(mbi_val=6, climate_val=3))
    assert result["climate_score"] == 50.0
