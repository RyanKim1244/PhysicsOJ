"""Pydantic schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field


# ===== Competition =====

class CompetitionOut(BaseModel):
    id: int
    name: str
    abbreviation: str
    country: str
    description: str
    website: str
    problem_count: int = 0

    model_config = {"from_attributes": True}


# ===== Problem =====

class ProblemSummary(BaseModel):
    """문제 목록용 요약"""
    id: int
    competition_name: str
    competition_abbr: str
    year: int
    problem_number: int
    title: str
    difficulty: str
    topic: str
    points: float
    solved_count: int = 0

    model_config = {"from_attributes": True}


class ProblemDetail(BaseModel):
    """문제 상세"""
    id: int
    competition_name: str
    competition_abbr: str
    year: int
    problem_number: int
    title: str
    description: str
    answer_type: str
    difficulty: str
    topic: str
    points: float
    hints: list[str] = []
    solved_count: int = 0

    model_config = {"from_attributes": True}


class ProblemWithSolution(ProblemDetail):
    """풀이 포함"""
    solution: str
    answer_data: str


# ===== Submission =====

class SubmissionCreate(BaseModel):
    """답안 제출 요청"""
    problem_id: int
    username: str = "guest"
    answer: str


class SubmissionResult(BaseModel):
    """채점 결과"""
    id: int
    problem_id: int
    problem_title: str
    status: str
    score: float
    max_score: float
    feedback: str
    submitted_at: datetime

    model_config = {"from_attributes": True}


class SubmissionHistory(BaseModel):
    """제출 이력"""
    id: int
    problem_id: int
    problem_title: str
    status: str
    score: float
    submitted_at: datetime

    model_config = {"from_attributes": True}


# ===== Stats =====

class UserStats(BaseModel):
    username: str
    total_submissions: int
    correct_count: int
    total_score: float
    accuracy: float
    problems_attempted: int
    problems_solved: int


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    display_name: str
    total_score: float
    problems_solved: int
