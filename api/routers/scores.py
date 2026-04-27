import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func

from database import get_session
from models.models import Score
from routers.admin import verify_admin_key
from schemas.schemas import ScoreRead, DepartmentAggregation

router = APIRouter()


@router.get("/scores", response_model=list[ScoreRead])
def list_scores(
    survey_id: UUID,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    return session.exec(
        select(Score).where(Score.survey_id == survey_id)
    ).all()


@router.get("/scores/by-department", response_model=list[DepartmentAggregation])
def scores_by_department(
    survey_id: UUID,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    scores = session.exec(
        select(Score).where(Score.survey_id == survey_id)
    ).all()

    if not scores:
        return []

    # Group by department
    by_dept: dict[str, list[Score]] = {}
    for s in scores:
        by_dept.setdefault(s.department, []).append(s)

    result = []
    for dept, dept_scores in by_dept.items():
        n = len(dept_scores)
        avg_exhaustion = sum(s.exhaustion_score for s in dept_scores) / n
        avg_depersonalization = sum(s.depersonalization_score for s in dept_scores) / n
        avg_achievement = sum(s.personal_achievement_score for s in dept_scores) / n
        avg_climate = sum(s.climate_score for s in dept_scores) / n

        # Dominant risk: most common risk_level
        from collections import Counter
        risk_counts = Counter(s.risk_level for s in dept_scores)
        dominant_risk = risk_counts.most_common(1)[0][0]

        result.append(DepartmentAggregation(
            department=dept,
            avg_exhaustion=round(avg_exhaustion, 2),
            avg_depersonalization=round(avg_depersonalization, 2),
            avg_achievement=round(avg_achievement, 2),
            avg_climate=round(avg_climate, 2),
            count=n,
            dominant_risk=dominant_risk,
        ))

    return result


@router.get("/scores/export")
def export_scores_csv(
    survey_id: UUID,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    scores = session.exec(
        select(Score).where(Score.survey_id == survey_id)
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "department", "exhaustion", "depersonalization",
        "achievement", "climate", "risk_level", "created_at"
    ])
    for s in scores:
        writer.writerow([
            s.department,
            s.exhaustion_score,
            s.depersonalization_score,
            s.personal_achievement_score,
            s.climate_score,
            s.risk_level,
            s.created_at.isoformat(),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scores_{survey_id}.csv"},
    )
