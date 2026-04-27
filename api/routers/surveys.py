from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from database import get_session
from models.models import Employee, Response, Score, Survey
from schemas.schemas import SurveySubmitRequest, ScoreRead
from services.scoring import calculate_scores
from services.tokens import verify_token
from services.alerts import check_and_create_alerts

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/surveys/{survey_id}", response_class=HTMLResponse)
def get_survey_form(
    survey_id: UUID,
    token: str,
    request: Request,
    session: Session = Depends(get_session),
):
    survey = session.get(Survey, survey_id)
    if not survey or survey.status != "active":
        raise HTTPException(status_code=404, detail="Survey not found or not active")

    employee = verify_token(token, session)
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid token")

    from constants import SURVEY_QUESTIONS
    return templates.TemplateResponse(
        "survey_form.html",
        {
            "request": request,
            "survey": survey,
            "questions": SURVEY_QUESTIONS,
            "token": token,
        },
    )


@router.post("/surveys/{survey_id}/respond", response_model=ScoreRead)
def submit_survey(
    survey_id: UUID,
    token: str,
    payload: SurveySubmitRequest,
    session: Session = Depends(get_session),
):
    survey = session.get(Survey, survey_id)
    if not survey or survey.status != "active":
        raise HTTPException(status_code=404, detail="Survey not found or not active")

    employee = verify_token(token, session)
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Check for duplicate response
    from sqlmodel import select
    existing = session.exec(
        select(Response).where(
            Response.survey_id == survey.id,
            Response.token_hash == employee.token_hash,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Survey already submitted for this token")

    # Save response
    response = Response(
        survey_id=survey.id,
        token_hash=employee.token_hash,
        department=employee.department,
        answers=payload.answers,
    )
    session.add(response)

    # Calculate and save scores
    scores_data = calculate_scores(payload.answers)
    score = Score(
        survey_id=survey.id,
        token_hash=employee.token_hash,
        department=employee.department,
        **scores_data,
    )
    session.add(score)
    session.commit()
    session.refresh(score)

    # Check and create alerts asynchronously (best-effort)
    check_and_create_alerts(survey.id, employee.department, session)

    return score
