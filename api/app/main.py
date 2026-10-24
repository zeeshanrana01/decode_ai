import sys
import json
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure parent 'api' directory is on sys.path for direct python execution
_API_DIR = Path(__file__).resolve().parent.parent
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from typing import List, Optional
from fastapi import FastAPI, Depends, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.config import OLLAMA_MODEL, GLOSSARY_FILE
from app.database import create_db_and_tables, get_session
from app.models.db import HistoryItem, QuizGradeRecord, HITLRequest, UserProfile
from app.models.schemas import (
    QuizSubmission,
    QuizGradeResult,
    HITLDecision,
    UserStatsResponse,
)
from app.agent.tools import GLOSSARY
from app.agent.agent import explain_term
from app.services.quiz_grader import grade_quiz
from app.services.stream import generate_explanation_stream
from app.services.gamification import (
    get_or_create_user,
    get_user_stats,
    ALL_AVAILABLE_BADGES,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="DecodeAI API",
    description="Student-friendly AI Term Explainer with LangChain agent, gamification, and guardrails",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "app": "DecodeAI",
        "description": "AI Term Explainer for School Students",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "glossary_count": len(GLOSSARY),
        "glossary_file": str(GLOSSARY_FILE),
        "model": OLLAMA_MODEL,
    }


@app.get("/api/glossary")
def get_glossary_terms():
    """Returns all glossary terms for search autocomplete and browsing."""
    terms_list = []
    for k, v in sorted(GLOSSARY.items()):
        terms_list.append({"term": k.title(), "key": k, "definition": v})
    return {"total": len(terms_list), "terms": terms_list}


@app.get("/api/explain/stream")
async def explain_stream(
    request: Request,
    term: str = Query(..., min_length=1, max_length=150),
    user_id: str = Query("student_1"),
    allow_web_search: bool = Query(False),
    session: Session = Depends(get_session),
):
    """
    Streams the agent explanation pipeline via Server-Sent Events (SSE).
    """
    client_ip = request.client.host if request.client else "unknown"

    return StreamingResponse(
        generate_explanation_stream(
            term=term,
            user_id=user_id,
            allow_web_search=allow_web_search,
            client_ip=client_ip,
            session=session,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/quiz/grade", response_model=QuizGradeResult)
def submit_quiz_answer(
    payload: QuizSubmission,
    session: Session = Depends(get_session),
):
    """
    Evaluates student quiz answer on a 0-3 scale with encouraging feedback.
    """
    return grade_quiz(
        term=payload.term,
        question=payload.quiz,
        user_answer=payload.user_answer,
        user_id=payload.user_id,
        session=session,
    )


@app.post("/api/hitl/approve")
def handle_hitl_approval(
    payload: HITLDecision,
    session: Session = Depends(get_session),
):
    """
    Human-in-the-loop decision for safe web search.
    """
    req = session.get(HITLRequest, payload.request_id)
    if not req:
        raise HTTPException(status_code=404, detail="HITL request not found")

    req.status = "approved" if payload.decision == "approve" else "rejected"
    if payload.edited_query:
        req.query = payload.edited_query

    session.add(req)
    session.commit()
    session.refresh(req)

    return {
        "status": req.status,
        "request_id": req.id,
        "query": req.query,
    }


@app.get("/api/user/stats", response_model=UserStatsResponse)
def get_stats(
    user_id: str = Query("student_1"),
    session: Session = Depends(get_session),
):
    """Returns current XP, level, streak, daily goal progress, and badges."""
    return get_user_stats(session, user_id)


@app.post("/api/user/freeze/buy")
def buy_streak_freeze(
    user_id: str = Query("student_1"),
    session: Session = Depends(get_session),
):
    """Claims or buys an extra streak freeze."""
    user = get_or_create_user(session, user_id)
    if user.credits < 5:
        raise HTTPException(status_code=400, detail="Requires 5 credits to claim a streak freeze!")

    user.credits -= 5
    user.streak_freezes += 1
    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "streak_freezes": user.streak_freezes,
        "remaining_credits": user.credits,
        "message": "❄️ Streak freeze acquired!",
    }


@app.get("/api/history")
def get_history(
    user_id: str = Query("student_1"),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Returns past term explanations and quiz results."""
    history = session.exec(
        select(HistoryItem)
        .where(HistoryItem.user_id == user_id)
        .order_by(HistoryItem.created_at.desc())
        .limit(limit)
    ).all()

    items = []
    for h in history:
        steps = []
        try:
            steps = json.loads(h.steps_json)
        except Exception:
            pass

        items.append({
            "id": h.id,
            "term": h.term,
            "simple": h.simple,
            "mental_model": h.mental_model,
            "steps": steps,
            "example": h.example,
            "quiz": h.quiz,
            "from_glossary": h.from_glossary,
            "used_web_search": h.used_web_search,
            "created_at": h.created_at.isoformat(),
        })

    quizzes = session.exec(
        select(QuizGradeRecord)
        .where(QuizGradeRecord.user_id == user_id)
        .order_by(QuizGradeRecord.created_at.desc())
        .limit(limit)
    ).all()

    quiz_items = []
    for q in quizzes:
        quiz_items.append({
            "id": q.id,
            "term": q.term,
            "question": q.quiz_question,
            "user_answer": q.user_answer,
            "score": q.score,
            "feedback": q.feedback,
            "xp_awarded": q.xp_awarded,
            "created_at": q.created_at.isoformat(),
        })

    return {
        "history": items,
        "quizzes": quiz_items,
    }


# CLI entrypoint matching original starter script style
if __name__ == "__main__":
    query_term = sys.argv[1] if len(sys.argv) > 1 else input("Term: ").strip()

    if not query_term:
        print("Please provide a term to explain.")
        sys.exit(0)

    print(f"\n🔍 Explaining: {query_term}")
    res = explain_term(query_term)

    print(f"\nTerm: {res.term}")
    print(f"Simple: {res.simple}")
    print(f"Mental model: {res.mental_model}")
    print("3 Steps:")
    for step in res.steps:
        print(f"  {step}")
    print(f"Example: {res.example}")
    print(f"Quiz: {res.quiz}")
    print(f"Source: {'AI glossary' if res.from_glossary else 'LLM knowledge'}")