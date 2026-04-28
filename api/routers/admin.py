from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from config import settings
from models.models import Survey, Employee
from schemas.schemas import (
    SurveyCreate, SurveyRead, SurveyStatusUpdate,
    TokenGenerateRequest, TokenGenerateResponse,
    AlertRead,
)
from services.tokens import generate_tokens, hash_token

router = APIRouter()


def verify_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key")
    return x_admin_key


@router.post("/surveys", response_model=SurveyRead, status_code=status.HTTP_201_CREATED)
def create_survey(
    payload: SurveyCreate,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    survey = Survey(**payload.model_dump())
    session.add(survey)
    session.commit()
    session.refresh(survey)
    return survey


@router.get("/surveys", response_model=list[SurveyRead])
def list_surveys(
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    return session.exec(select(Survey)).all()


@router.patch("/surveys/{survey_id}/status", response_model=SurveyRead)
def update_survey_status(
    survey_id: UUID,
    payload: SurveyStatusUpdate,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    survey = session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    survey.status = payload.status
    session.add(survey)
    session.commit()
    session.refresh(survey)
    return survey


@router.post("/surveys/{survey_id}/tokens", response_model=TokenGenerateResponse)
def generate_survey_tokens(
    survey_id: UUID,
    payload: TokenGenerateRequest,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    survey = session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    tokens = generate_tokens(payload.count)
    for token in tokens:
        employee = Employee(
            token_hash=hash_token(token),
            department=payload.department,
        )
        session.add(employee)
    session.commit()

    return TokenGenerateResponse(
        tokens=tokens,
        department=payload.department,
        count=len(tokens),
    )


@router.get("/alerts", response_model=list[AlertRead])
def list_alerts(
    seen: bool | None = None,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    from models.models import Alert
    query = select(Alert)
    if seen is not None:
        query = query.where(Alert.seen == seen)
    return session.exec(query).all()


@router.patch("/alerts/{alert_id}/seen", response_model=AlertRead)
def mark_alert_seen(
    alert_id: UUID,
    session: Session = Depends(get_session),
    _: str = Depends(verify_admin_key),
):
    from models.models import Alert
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.seen = True
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert
