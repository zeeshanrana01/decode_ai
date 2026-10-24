from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserProfile(SQLModel, table=True):
    id: str = Field(default="student_1", primary_key=True)
    name: str = Field(default="Curious Student")
    xp: int = Field(default=0)
    level: int = Field(default=1)
    level_title: str = Field(default="Curious Spark")
    streak_count: int = Field(default=1)
    streak_freezes: int = Field(default=2)
    credits: int = Field(default=20)
    last_active_date: str = Field(default="")
    last_credit_refresh: str = Field(default="")
    created_at: datetime = Field(default_factory=utc_now)


class Badge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    badge_key: str = Field(index=True)
    name: str
    description: str
    icon: str
    unlocked_at: datetime = Field(default_factory=utc_now)


class DailyGoal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    date_str: str = Field(index=True)
    terms_count: int = Field(default=0)
    target_terms: int = Field(default=3)
    quizzes_count: int = Field(default=0)
    target_quizzes: int = Field(default=1)
    completed: bool = Field(default=False)
    bonus_collected: bool = Field(default=False)


class HistoryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    term: str = Field(index=True)
    simple: str
    mental_model: str
    steps_json: str = Field(default="[]")
    example: str
    quiz: str
    from_glossary: bool = Field(default=False)
    used_web_search: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)


class QuizGradeRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    term: str = Field(index=True)
    quiz_question: str
    user_answer: str
    score: int  # 0 to 3
    feedback: str
    xp_awarded: int
    created_at: datetime = Field(default_factory=utc_now)


class HITLRequest(SQLModel, table=True):
    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    action: str = Field(default="safe_web_search")
    query: str
    reason: str
    status: str = Field(default="pending")  # pending, approved, rejected
    created_at: datetime = Field(default_factory=utc_now)
