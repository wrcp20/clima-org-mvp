import pytest
from services.scoring import calculate_scores


def _base_answers(mbi_val: int = 0, climate_val: int = 1) -> dict[str, int]:
    answers = {f"q{i}": mbi_val for i in range(1, 10)}
    answers.update({f"q{i}": climate_val for i in range(10, 16)})
    return answers


def test_all_zeros_mbi_min_climate():
    answers = _base_answers(mbi_val=0, climate_val=1)
    result = calculate_scores(answers)
    assert result["exhaustion_score"] == 0
    assert result["depersonalization_score"] == 0
    assert result["personal_achievement_score"] == 12  # 6-0=6, x2
    assert result["climate_score"] == 0.0              # (1-1)/4*100
    assert result["risk_level"] == "medium"            # achievement=12 >= 8


def test_all_max_values():
    answers = _base_answers(mbi_val=6, climate_val=5)
    result = calculate_scores(answers)
    assert result["exhaustion_score"] == 30
    assert result["depersonalization_score"] == 12
    assert result["personal_achievement_score"] == 0   # 6-6=0
    assert result["climate_score"] == 100.0
    assert result["risk_level"] == "high"              # exhaustion + depersonalization


def test_exactly_one_dimension_at_risk():
    answers = {f"q{i}": 4 for i in range(1, 6)}       # exhaustion=20 (at threshold)
    answers.update({f"q{i}": 0 for i in range(6, 10)})
    answers.update({f"q{i}": 3 for i in range(10, 16)})
    result = calculate_scores(answers)
    assert result["exhaustion_score"] == 20
    assert result["depersonalization_score"] == 0
    assert result["personal_achievement_score"] == 12  # 6-0=6 x2, but wait...
    # achievement=12 >= 8, so actually 2 dimensions at risk → high
    # Let's use q8=q9=6 so achievement=0
    answers[f"q8"] = 6
    answers[f"q9"] = 6
    result2 = calculate_scores(answers)
    assert result2["exhaustion_score"] == 20
    assert result2["personal_achievement_score"] == 0
    assert result2["risk_level"] == "medium"           # only exhaustion at risk


def test_exactly_two_dimensions_at_risk():
    answers = {f"q{i}": 4 for i in range(1, 6)}       # exhaustion=20
    answers.update({f"q{i}": 4 for i in range(6, 8)}) # depersonalization=8
    answers.update({f"q{i}": 6 for i in range(8, 10)})# achievement=0 (not at risk)
    answers.update({f"q{i}": 3 for i in range(10, 16)})
    result = calculate_scores(answers)
    assert result["exhaustion_score"] == 20
    assert result["depersonalization_score"] == 8
    assert result["personal_achievement_score"] == 0
    assert result["risk_level"] == "high"


def test_climate_score_maximum():
    answers = _base_answers(mbi_val=0, climate_val=5)
    result = calculate_scores(answers)
    assert result["climate_score"] == 100.0


def test_climate_score_minimum():
    answers = _base_answers(mbi_val=0, climate_val=1)
    result = calculate_scores(answers)
    assert result["climate_score"] == 0.0
