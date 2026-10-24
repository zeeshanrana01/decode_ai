from app.services.gamification import (
    get_or_create_user,
    add_xp,
    update_streak,
    calculate_level,
    get_or_create_daily_goal,
    record_daily_term,
    record_daily_quiz,
    check_and_unlock_badges,
    get_user_stats,
    ALL_AVAILABLE_BADGES,
)
from app.services.quiz_grader import grade_quiz
from app.services.stream import generate_explanation_stream

__all__ = [
    "get_or_create_user",
    "add_xp",
    "update_streak",
    "calculate_level",
    "get_or_create_daily_goal",
    "record_daily_term",
    "record_daily_quiz",
    "check_and_unlock_badges",
    "get_user_stats",
    "ALL_AVAILABLE_BADGES",
    "grade_quiz",
    "generate_explanation_stream",
]
