"""Submissions API endpoints - 답안 제출 및 채점."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import Problem, User, Submission, SubmissionStatus
from app.schemas import SubmissionCreate, SubmissionResult, SubmissionHistory
from app.services.judge import judge

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionResult)
def submit_answer(submission: SubmissionCreate, db: Session = Depends(get_db)):
    """답안 제출 및 즉시 채점"""
    # 문제 조회
    problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    # 사용자 조회 또는 생성
    user = db.query(User).filter(User.username == submission.username).first()
    if not user:
        user = User(username=submission.username, display_name=submission.username)
        db.add(user)
        db.flush()

    # 채점
    result = judge(
        user_answer=submission.answer,
        answer_type=problem.answer_type.value,
        answer_data_json=problem.answer_data,
        tolerance=problem.tolerance,
        max_points=problem.points,
    )

    # 상태 결정
    if result.is_correct:
        status = SubmissionStatus.CORRECT
    elif result.score > 0:
        status = SubmissionStatus.PARTIAL
    else:
        status = SubmissionStatus.WRONG

    # 제출 기록 저장
    db_submission = Submission(
        user_id=user.id,
        problem_id=problem.id,
        answer=submission.answer,
        status=status,
        score=result.score,
        feedback=result.feedback,
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    return SubmissionResult(
        id=db_submission.id,
        problem_id=problem.id,
        problem_title=problem.title,
        status=status.value,
        score=result.score,
        max_score=result.max_score,
        feedback=result.feedback,
        submitted_at=db_submission.submitted_at,
    )


@router.get("/history/{username}", response_model=list[SubmissionHistory])
def get_submission_history(username: str, db: Session = Depends(get_db)):
    """사용자의 제출 이력 조회"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    submissions = (
        db.query(Submission)
        .filter(Submission.user_id == user.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )

    return [
        SubmissionHistory(
            id=s.id,
            problem_id=s.problem_id,
            problem_title=s.problem.title,
            status=s.status.value,
            score=s.score,
            submitted_at=s.submitted_at,
        )
        for s in submissions
    ]
