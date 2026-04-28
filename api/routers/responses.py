from uuid import UUID
from collections import Counter

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from database import get_session
from models.models import Response
from routers.admin import verify_admin_key
from schemas.schemas import ResponseSummary

router = APIRouter()


@router.get("/responses/summary", response_model=list[ResponseSummary])
def responses_summary(
    survey_id: UUID,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    responses = session.exec(
        select(Response).where(Response.survey_id == survey_id)
    ).all()

    counts = Counter(r.department for r in responses)
    return [
        ResponseSummary(department=dept, response_count=count)
        for dept, count in sorted(counts.items())
    ]
