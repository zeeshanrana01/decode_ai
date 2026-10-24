import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.database import get_session
from app.models.db import HITLRequest


from sqlalchemy.pool import StaticPool

# Setup test SQLite database with StaticPool for thread-safe in-memory testing
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(test_engine)


def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "DecodeAI"


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["glossary_count"] > 0


def test_glossary():
    response = client.get("/api/glossary")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert isinstance(data["terms"], list)


def test_user_stats():
    response = client.get("/api/user/stats?user_id=test_student_api")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test_student_api"
    assert data["level"] == 1
    assert data["credits"] > 0
    assert "badges" in data


def test_quiz_grading():
    payload = {
        "term": "RAG",
        "quiz": "Why is RAG like an open-book exam? A) It looks up trustworthy source documents before writing",
        "user_answer": "It looks up documents in the library before generating an answer so it stays accurate.",
        "user_id": "test_student_quiz",
    }
    response = client.post("/api/quiz/grade", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["score"] <= 3
    assert len(data["feedback"]) > 5
    assert data["xp_awarded"] > 0


def test_hitl_approval():
    # Insert a dummy HITL request in test DB
    with Session(test_engine) as session:
        req = HITLRequest(
            id="hitl_test_1",
            user_id="test_student_api",
            action="safe_web_search",
            query="neuromorphic computing",
            reason="not in glossary",
            status="pending",
        )
        session.add(req)
        session.commit()

    payload = {
        "request_id": "hitl_test_1",
        "decision": "approve",
        "user_id": "test_student_api",
    }
    response = client.post("/api/hitl/approve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


def test_history():
    response = client.get("/api/history?user_id=test_student_quiz")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert "quizzes" in data
    assert len(data["quizzes"]) >= 1


def test_explain_stream_sse():
    response = client.get("/api/explain/stream?term=RAG&user_id=test_student_sse")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    text = response.text
    assert "event: status" in text
    assert "event: explanation" in text
    assert "event: gamification" in text
    assert "event: done" in text
