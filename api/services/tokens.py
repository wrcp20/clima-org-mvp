import hashlib
import secrets

from sqlmodel import Session, select

from models.models import Employee


def generate_tokens(count: int) -> list[str]:
    return [secrets.token_urlsafe(32) for _ in range(count)]


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str, session: Session) -> Employee | None:
    token_hash = hash_token(token)
    return session.exec(
        select(Employee).where(Employee.token_hash == token_hash)
    ).first()
