"""Competitions API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Competition
from app.schemas import CompetitionOut

router = APIRouter(prefix="/api/competitions", tags=["competitions"])


@router.get("", response_model=list[CompetitionOut])
def list_competitions(db: Session = Depends(get_db)):
    """등록된 대회 목록"""
    competitions = db.query(Competition).order_by(Competition.abbreviation).all()
    return [
        CompetitionOut(
            id=c.id,
            name=c.name,
            abbreviation=c.abbreviation,
            country=c.country,
            description=c.description,
            website=c.website,
            problem_count=len(c.problems),
        )
        for c in competitions
    ]
