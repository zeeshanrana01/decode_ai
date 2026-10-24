import pytest
from datetime import date, timedelta
from sqlmodel import SQLModel, Session, create_engine

from app.models.db import UserProfile, Badge, DailyGoal, HistoryItem, QuizGradeRecord
from app.services.gamification import (
    get_or_create_user,
    add_xp,
    update_streak,
    calculate_level,
    record_daily_term,
    record_daily_quiz,
    check_and_unlock_badges,
    get_user_stats,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_level_calculation():
    lvl, title, in_lvl, high, pct = calculate_level(0)
    assert lvl == 1
    assert title == "Curious Spark"

    lvl, title, in_lvl, high, pct = calculate_level(120)
    assert lvl == 2
    assert title == "Prompt Explorer"

    lvl, title, in_lvl, high, pct = calculate_level(300)
    assert lvl == 3
    assert title == "Neural Cadet"


def test_add_xp_and_level_up(session: Session):
    user = get_or_create_user(session, "student_test_1")
    assert user.xp == 0
    assert user.level == 1

    leveled_up, new_lvl, new_title = add_xp(session, user, 150)
    assert user.xp == 150
    assert leveled_up is True
    assert new_lvl == 2
    assert new_title == "Prompt Explorer"


def test_streak_consecutive_days(session: Session):
    user = get_or_create_user(session, "student_streak_1")
    user.streak_count = 1
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    user.last_active_date = yesterday

    msg = update_streak(user, date.today().isoformat())
    assert user.streak_count == 2
    assert msg is None


def test_streak_freeze_activation(session: Session):
    user = get_or_create_user(session, "student_freeze_1")
    user.streak_count = 5
    user.streak_freezes = 2
    # Missed 1 day (last active 2 days ago)
    two_days_ago = (date.today() - timedelta(days=2)).isoformat()
    user.last_active_date = two_days_ago

    msg = update_streak(user, date.today().isoformat())
    # Streak should be preserved and 1 freeze deducted
    assert user.streak_count == 5
    assert user.streak_freezes == 1
    assert "Streak Freeze activated" in msg


def test_daily_goal_completion(session: Session):
    uid = "student_goal_1"
    goal, completed = record_daily_term(session, uid)
    assert goal.terms_count == 1
    assert completed is False

    record_daily_term(session, uid)
    record_daily_term(session, uid)  # terms_count reaches 3

    # Now complete 1 quiz to trigger full daily goal
    goal, completed_now = record_daily_quiz(session, uid)
    assert completed_now is True
    assert goal.completed is True
    assert goal.bonus_collected is True


def test_badge_unlock(session: Session):
    uid = "student_badge_1"
    user = get_or_create_user(session, uid)

    # Initially no badges
    badges = check_and_unlock_badges(session, uid)
    assert len(badges) == 0

    # Add 1 history item
    h = HistoryItem(
        user_id=uid,
        term="Token",
        simple="A word chunk",
        mental_model="Lego brick",
        steps_json="[]",
        example="Cat is 1 token",
        quiz="What is token?",
        from_glossary=True,
    )
    session.add(h)
    session.commit()

    # Now First Spark badge should unlock
    unlocked = check_and_unlock_badges(session, uid)
    assert len(unlocked) == 1
    assert unlocked[0].badge_key == "first_spark"
