from uuid import UUID

from sqlmodel import Session, select

from models.models import Alert, Score


THRESHOLDS = {
    "exhaustion": 20.0,
    "depersonalization": 8.0,
    "achievement": 8.0,
    "climate": 40.0,
}


def check_and_create_alerts(
    survey_id: UUID, department: str, session: Session
) -> list[Alert]:
    scores = session.exec(
        select(Score).where(
            Score.survey_id == survey_id,
            Score.department == department,
        )
    ).all()

    if not scores:
        return []

    count = len(scores)
    avg = {
        "exhaustion": sum(s.exhaustion_score for s in scores) / count,
        "depersonalization": sum(s.depersonalization_score for s in scores) / count,
        "achievement": sum(s.personal_achievement_score for s in scores) / count,
        "climate": sum(s.climate_score for s in scores) / count,
    }

    created = []
    for score_type, threshold in THRESHOLDS.items():
        value = avg[score_type]
        # climate: alert when BELOW threshold (low climate = bad)
        triggered = value <= threshold if score_type == "climate" else value >= threshold
        if triggered:
            alert = Alert(
                department=department,
                score_type=score_type,
                value=round(value, 2),
                threshold=threshold,
            )
            session.add(alert)
            created.append(alert)

    session.commit()
    return created
