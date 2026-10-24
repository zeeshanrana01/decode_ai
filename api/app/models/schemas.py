from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class TermExplanation(BaseModel):
    term: str = Field(description="The AI term being explained")
    simple: str = Field(description="One easy sentence a beginner understands")
    mental_model: str = Field(
        description="An everyday analogy that makes the idea click, e.g. 'RAG is like an open-book exam'"
    )
    steps: List[str] = Field(
        default_factory=list,
        description="Exactly 3 simple steps explaining how this mental model / concept works in action"
    )
    example: str = Field(description="One real-life example relatable to students")
    quiz: str = Field(description="One short question to test the learner")
    from_glossary: bool = Field(description="True if the definition came from the glossary")
    used_web_search: bool = Field(default=False, description="True if safe web search was approved and used")


class ExplainRequest(BaseModel):
    term: str = Field(min_length=1, max_length=100)
    user_id: str = Field(default="student_1")
    allow_web_search: bool = Field(default=False)


class QuizSubmission(BaseModel):
    term: str
    quiz: str
    user_answer: str = Field(min_length=1, max_length=500)
    user_id: str = Field(default="student_1")


class QuizGradeResult(BaseModel):
    score: int = Field(ge=0, le=3, description="Score from 0 (incorrect) to 3 (mastery)")
    feedback: str = Field(description="Encouraging feedback for a school student")
    xp_awarded: int
    badge_unlocked: Optional[str] = None
    streak_bonus: bool = False
    new_level: Optional[int] = None


class HITLDecision(BaseModel):
    request_id: str
    decision: str = Field(description="'approve', 'reject', or 'edit'")
    user_id: str = Field(default="student_1")
    edited_query: Optional[str] = None


class BadgeItem(BaseModel):
    badge_key: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: Optional[datetime] = None


class UserStatsResponse(BaseModel):
    id: str
    name: str
    xp: int
    level: int
    level_title: str
    xp_in_level: int
    xp_for_next_level: int
    progress_percent: float
    streak_count: int
    streak_freezes: int
    credits: int
    daily_goal: dict[str, Any]
    badges: List[BadgeItem]
