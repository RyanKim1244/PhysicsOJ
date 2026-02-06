"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.services.seed_data import seed_all

# Test DB
TEST_DATABASE_URL = "sqlite:///./test_opc.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    seed_all(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


class TestCompetitionsAPI:
    def test_list_competitions(self):
        res = client.get("/api/competitions")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 5
        abbrs = [c["abbreviation"] for c in data]
        assert "IPhO" in abbrs
        assert "KPhO" in abbrs

    def test_competition_has_problem_count(self):
        res = client.get("/api/competitions")
        data = res.json()
        ipho = next(c for c in data if c["abbreviation"] == "IPhO")
        assert ipho["problem_count"] > 0


class TestProblemsAPI:
    def test_list_problems(self):
        res = client.get("/api/problems")
        assert res.status_code == 200
        data = res.json()
        assert len(data) > 0

    def test_filter_by_competition(self):
        res = client.get("/api/problems?competition=KPhO")
        assert res.status_code == 200
        data = res.json()
        assert all(p["competition_abbr"] == "KPhO" for p in data)

    def test_filter_by_topic(self):
        res = client.get("/api/problems?topic=역학")
        assert res.status_code == 200
        data = res.json()
        assert all(p["topic"] == "역학" for p in data)

    def test_get_problem_detail(self):
        # Get first problem id
        problems = client.get("/api/problems").json()
        pid = problems[0]["id"]

        res = client.get(f"/api/problems/{pid}")
        assert res.status_code == 200
        data = res.json()
        assert "description" in data
        assert "answer_type" in data

    def test_get_nonexistent_problem(self):
        res = client.get("/api/problems/99999")
        assert res.status_code == 404

    def test_get_solution(self):
        problems = client.get("/api/problems").json()
        pid = problems[0]["id"]

        res = client.get(f"/api/problems/{pid}/solution")
        assert res.status_code == 200
        data = res.json()
        assert "solution" in data

    def test_list_topics(self):
        res = client.get("/api/problems/topics")
        assert res.status_code == 200
        data = res.json()
        assert "역학" in data


class TestSubmissionsAPI:
    def test_submit_correct_answer(self):
        # Find the simple pendulum problem (answer: 2.838)
        problems = client.get("/api/problems").json()
        pendulum = next(p for p in problems if "단진자" in p["title"])

        res = client.post("/api/submissions", json={
            "problem_id": pendulum["id"],
            "username": "testuser",
            "answer": "2.838",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "correct"
        assert data["score"] > 0

    def test_submit_wrong_answer(self):
        problems = client.get("/api/problems").json()
        pendulum = next(p for p in problems if "단진자" in p["title"])

        res = client.post("/api/submissions", json={
            "problem_id": pendulum["id"],
            "username": "testuser",
            "answer": "99.99",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "wrong"

    def test_submit_multiple_choice(self):
        problems = client.get("/api/problems").json()
        mc_problem = next(p for p in problems if "경사면" in p["title"])

        res = client.post("/api/submissions", json={
            "problem_id": mc_problem["id"],
            "username": "testuser",
            "answer": "A",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "correct"

    def test_submit_creates_user(self):
        problems = client.get("/api/problems").json()
        pid = problems[0]["id"]

        res = client.post("/api/submissions", json={
            "problem_id": pid,
            "username": "newuser123",
            "answer": "0",
        })
        assert res.status_code == 200

        # Check history
        history_res = client.get("/api/submissions/history/newuser123")
        assert history_res.status_code == 200
        assert len(history_res.json()) > 0

    def test_submit_nonexistent_problem(self):
        res = client.post("/api/submissions", json={
            "problem_id": 99999,
            "username": "testuser",
            "answer": "42",
        })
        assert res.status_code == 404

    def test_submission_history(self):
        # Make a submission first
        problems = client.get("/api/problems").json()
        client.post("/api/submissions", json={
            "problem_id": problems[0]["id"],
            "username": "historyuser",
            "answer": "42",
        })

        res = client.get("/api/submissions/history/historyuser")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1


class TestStatsAPI:
    def test_user_stats(self):
        # Make some submissions
        problems = client.get("/api/problems").json()
        client.post("/api/submissions", json={
            "problem_id": problems[0]["id"],
            "username": "statsuser",
            "answer": "42",
        })

        res = client.get("/api/stats/user/statsuser")
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == "statsuser"
        assert data["total_submissions"] >= 1

    def test_user_stats_not_found(self):
        res = client.get("/api/stats/user/nonexistent_user")
        assert res.status_code == 404

    def test_leaderboard(self):
        res = client.get("/api/stats/leaderboard")
        assert res.status_code == 200
        assert isinstance(res.json(), list)
