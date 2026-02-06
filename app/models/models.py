"""SQLAlchemy ORM models for the Physics Online Judge."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class Difficulty(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    OLYMPIAD = "olympiad"


class SubmissionStatus(enum.Enum):
    PENDING = "pending"
    CORRECT = "correct"
    WRONG = "wrong"
    PARTIAL = "partial"
    ERROR = "error"


class AnswerType(enum.Enum):
    NUMERIC = "numeric"           # 수치 답 (허용 오차 포함)
    EXPRESSION = "expression"     # 수식 답 (SymPy로 동치 비교)
    MULTIPLE_CHOICE = "multiple_choice"  # 객관식
    MULTI_PART = "multi_part"     # 여러 소문항


class Competition(Base):
    """물리 대회 정보"""
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    abbreviation = Column(String(20), nullable=False)  # e.g. IPhO, KPhO, APhO
    country = Column(String(100), default="International")
    description = Column(Text, default="")
    website = Column(String(500), default="")

    problems = relationship("Problem", back_populates="competition")


class Problem(Base):
    """물리 문제"""
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    year = Column(Integer, nullable=False)
    problem_number = Column(Integer, nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)       # 문제 본문 (Markdown/LaTeX)
    answer_type = Column(SAEnum(AnswerType), nullable=False)
    answer_data = Column(Text, nullable=False)        # JSON: 정답 데이터
    tolerance = Column(Float, default=0.01)           # 수치 답의 허용 오차 (상대 오차)
    points = Column(Float, default=10.0)              # 배점
    difficulty = Column(SAEnum(Difficulty), default=Difficulty.MEDIUM)
    topic = Column(String(100), default="general")    # 역학, 전자기학, 열역학, 광학, 현대물리 등
    solution = Column(Text, default="")               # 풀이 (Markdown/LaTeX)
    hints = Column(Text, default="")                  # 힌트 (JSON array)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    competition = relationship("Competition", back_populates="problems")
    submissions = relationship("Submission", back_populates="problem")


class User(Base):
    """사용자"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    submissions = relationship("Submission", back_populates="user")


class Submission(Base):
    """답안 제출"""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    answer = Column(Text, nullable=False)             # 사용자가 제출한 답
    status = Column(SAEnum(SubmissionStatus), default=SubmissionStatus.PENDING)
    score = Column(Float, default=0.0)                # 획득 점수
    feedback = Column(Text, default="")               # 채점 피드백
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
