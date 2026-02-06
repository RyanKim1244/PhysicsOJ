"""Problems API endpoints."""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import Problem, Competition, Submission, SubmissionStatus
from app.schemas import ProblemSummary, ProblemDetail, ProblemWithSolution

router = APIRouter(prefix="/api/problems", tags=["problems"])


def _get_solved_count(db: Session, problem_id: int) -> int:
    return db.query(func.count(Submission.id)).filter(
        Submission.problem_id == problem_id,
        Submission.status == SubmissionStatus.CORRECT
    ).scalar() or 0


@router.get("", response_model=list[ProblemSummary])
def list_problems(
    competition: str | None = Query(None, description="대회 약칭 필터 (e.g. IPhO)"),
    topic: str | None = Query(None, description="주제 필터 (e.g. 역학)"),
    difficulty: str | None = Query(None, description="난이도 필터"),
    year: int | None = Query(None, description="연도 필터"),
    db: Session = Depends(get_db),
):
    """문제 목록 조회"""
    query = db.query(Problem).join(Competition)

    if competition:
        query = query.filter(Competition.abbreviation == competition)
    if topic:
        query = query.filter(Problem.topic == topic)
    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)
    if year:
        query = query.filter(Problem.year == year)

    query = query.order_by(Competition.abbreviation, Problem.year.desc(), Problem.problem_number)
    problems = query.all()

    return [
        ProblemSummary(
            id=p.id,
            competition_name=p.competition.name,
            competition_abbr=p.competition.abbreviation,
            year=p.year,
            problem_number=p.problem_number,
            title=p.title,
            difficulty=p.difficulty.value,
            topic=p.topic,
            points=p.points,
            solved_count=_get_solved_count(db, p.id),
        )
        for p in problems
    ]


@router.get("/topics")
def list_topics(db: Session = Depends(get_db)):
    """사용 가능한 주제 목록"""
    topics = db.query(Problem.topic).distinct().order_by(Problem.topic).all()
    return [t[0] for t in topics]


@router.get("/{problem_id}", response_model=ProblemDetail)
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    """문제 상세 조회"""
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    hints = []
    if problem.hints:
        try:
            hints = json.loads(problem.hints)
        except json.JSONDecodeError:
            pass

    return ProblemDetail(
        id=problem.id,
        competition_name=problem.competition.name,
        competition_abbr=problem.competition.abbreviation,
        year=problem.year,
        problem_number=problem.problem_number,
        title=problem.title,
        description=problem.description,
        answer_type=problem.answer_type.value,
        difficulty=problem.difficulty.value,
        topic=problem.topic,
        points=problem.points,
        hints=hints,
        solved_count=_get_solved_count(db, problem.id),
    )


@router.get("/{problem_id}/solution", response_model=ProblemWithSolution)
def get_solution(problem_id: int, db: Session = Depends(get_db)):
    """문제 풀이 조회"""
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    hints = []
    if problem.hints:
        try:
            hints = json.loads(problem.hints)
        except json.JSONDecodeError:
            pass

    return ProblemWithSolution(
        id=problem.id,
        competition_name=problem.competition.name,
        competition_abbr=problem.competition.abbreviation,
        year=problem.year,
        problem_number=problem.problem_number,
        title=problem.title,
        description=problem.description,
        answer_type=problem.answer_type.value,
        difficulty=problem.difficulty.value,
        topic=problem.topic,
        points=problem.points,
        hints=hints,
        solved_count=_get_solved_count(db, problem.id),
        solution=problem.solution,
        answer_data=problem.answer_data,
    )
