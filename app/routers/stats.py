"""Statistics and leaderboard endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import User, Submission, SubmissionStatus
from app.schemas import UserStats, LeaderboardEntry

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/user/{username}", response_model=UserStats)
def get_user_stats(username: str, db: Session = Depends(get_db)):
    """사용자 통계"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    submissions = db.query(Submission).filter(Submission.user_id == user.id).all()
    total = len(submissions)
    correct = sum(1 for s in submissions if s.status == SubmissionStatus.CORRECT)
    total_score = sum(s.score for s in submissions)
    problems_attempted = len(set(s.problem_id for s in submissions))
    problems_solved = len(set(
        s.problem_id for s in submissions if s.status == SubmissionStatus.CORRECT
    ))

    return UserStats(
        username=user.username,
        total_submissions=total,
        correct_count=correct,
        total_score=total_score,
        accuracy=correct / total if total > 0 else 0.0,
        problems_attempted=problems_attempted,
        problems_solved=problems_solved,
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    """리더보드 - 총점 기준 정렬"""
    # 각 사용자별 최고 점수 제출만 합산 (문제당 최고 점수)
    results = (
        db.query(
            User.username,
            User.display_name,
            func.sum(Submission.score).label("total_score"),
            func.count(
                func.distinct(
                    Submission.problem_id
                )
            ).filter(Submission.status == SubmissionStatus.CORRECT).label("problems_solved"),
        )
        .join(Submission, User.id == Submission.user_id)
        .group_by(User.id)
        .order_by(func.sum(Submission.score).desc())
        .all()
    )

    return [
        LeaderboardEntry(
            rank=i + 1,
            username=r.username,
            display_name=r.display_name or r.username,
            total_score=r.total_score or 0,
            problems_solved=r.problems_solved or 0,
        )
        for i, r in enumerate(results)
    ]
