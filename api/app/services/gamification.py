from datetime import datetime, date, timedelta, timezone
from typing import List, Tuple, Optional, Dict, Any
from sqlmodel import Session, select

from app.models.db import UserProfile, Badge, DailyGoal, HistoryItem, QuizGradeRecord
from app.models.schemas import UserStatsResponse, BadgeItem
from app.config import (
    DEFAULT_DAILY_CREDITS,
    DEFAULT_STREAK_FREEZES,
    DAILY_GOAL_TERMS,
    DAILY_GOAL_QUIZZES,
    DAILY_GOAL_BONUS_XP,
)

LEVEL_THRESHOLDS = [
    (1, "Curious Spark", 0, 100),
    (2, "Prompt Explorer", 100, 250),
    (3, "Neural Cadet", 250, 500),
    (4, "Algorithm Knight", 500, 900),
    (5, "Byte Master", 900, 1500),
    (6, "AI Alchemist", 1500, 999999),
]

ALL_AVAILABLE_BADGES = [
    {"key": "first_spark", "name": "First Spark", "description": "Explained your very first AI term!", "icon": "⚡"},
    {"key": "glossary_worm", "name": "Bookworm", "description": "Explored 5 terms from the official Stanford HAI glossary!", "icon": "📚"},
    {"key": "quiz_wiz", "name": "Quiz Wiz", "description": "Scored a perfect 3/3 on an AI quiz!", "icon": "🎯"},
    {"key": "quiz_scholar", "name": "Scholar", "description": "Completed 3 AI knowledge quizzes!", "icon": "🎓"},
    {"key": "flame_keeper", "name": "Flame Keeper", "description": "Maintained an active 3-day learning streak!", "icon": "🔥"},
    {"key": "web_scout", "name": "Web Scout", "description": "Used safe educational web search for a new term!", "icon": "🌐"},
    {"key": "neural_cadet", "name": "Neural Cadet", "description": "Advanced to Level 3 in your AI journey!", "icon": "🤖"},
]


def today_str() -> str:
    return date.today().isoformat()


def get_or_create_user(session: Session, user_id: str = "student_1") -> UserProfile:
    user = session.get(UserProfile, user_id)
    now_date = today_str()

    if not user:
        user = UserProfile(
            id=user_id,
            name="Curious Student",
            xp=0,
            level=1,
            level_title="Curious Spark",
            streak_count=1,
            streak_freezes=DEFAULT_STREAK_FREEZES,
            credits=DEFAULT_DAILY_CREDITS,
            last_active_date=now_date,
            last_credit_refresh=now_date,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    # Check daily credit refresh
    if user.last_credit_refresh != now_date:
        user.credits = DEFAULT_DAILY_CREDITS
        user.last_credit_refresh = now_date

    # Update streak
    update_streak(user, now_date)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_streak(user: UserProfile, current_date_str: str) -> Optional[str]:
    """
    Updates streak logic:
    - Same day: no change
    - Yesterday: streak + 1
    - 2 days ago: streak freeze used if available, else resets to 1
    - > 2 days ago: resets to 1
    """
    if not user.last_active_date:
        user.last_active_date = current_date_str
        user.streak_count = 1
        return None

    if user.last_active_date == current_date_str:
        return None

    try:
        last_date = date.fromisoformat(user.last_active_date)
        curr_date = date.fromisoformat(current_date_str)
        diff_days = (curr_date - last_date).days

        if diff_days == 1:
            user.streak_count += 1
            user.last_active_date = current_date_str
            return None
        elif diff_days == 2:
            # Missed exactly 1 day
            if user.streak_freezes > 0:
                user.streak_freezes -= 1
                user.last_active_date = current_date_str
                return "❄️ Streak Freeze activated! Your learning streak was saved!"
            else:
                user.streak_count = 1
                user.last_active_date = current_date_str
                return "Streak reset to 1 day."
        else:
            user.streak_count = 1
            user.last_active_date = current_date_str
            return "Streak reset to 1 day."
    except Exception:
        user.last_active_date = current_date_str
        return None


def calculate_level(xp: int) -> Tuple[int, str, int, int, float]:
    """
    Returns (level, title, xp_in_level, xp_for_next, progress_percent).
    """
    for lvl, title, low, high in LEVEL_THRESHOLDS:
        if low <= xp < high:
            span = high - low
            in_level = xp - low
            pct = round((in_level / span) * 100, 1)
            return lvl, title, in_level, high, pct

    # Max level reached
    return 6, "AI Alchemist", xp, 1500, 100.0


def add_xp(session: Session, user: UserProfile, amount: int) -> Tuple[bool, int, str]:
    """
    Adds XP and handles level advancement.
    Returns (leveled_up, new_level, new_title).
    """
    old_level = user.level
    user.xp += amount
    new_lvl, new_title, _, _, _ = calculate_level(user.xp)

    user.level = new_lvl
    user.level_title = new_title
    session.add(user)
    session.commit()
    session.refresh(user)

    leveled_up = new_lvl > old_level
    return leveled_up, new_lvl, new_title


def get_or_create_daily_goal(session: Session, user_id: str) -> DailyGoal:
    now_date = today_str()
    statement = select(DailyGoal).where(DailyGoal.user_id == user_id, DailyGoal.date_str == now_date)
    goal = session.exec(statement).first()

    if not goal:
        goal = DailyGoal(
            user_id=user_id,
            date_str=now_date,
            terms_count=0,
            target_terms=DAILY_GOAL_TERMS,
            quizzes_count=0,
            target_quizzes=DAILY_GOAL_QUIZZES,
            completed=False,
            bonus_collected=False,
        )
        session.add(goal)
        session.commit()
        session.refresh(goal)

    return goal


def record_daily_term(session: Session, user_id: str) -> Tuple[DailyGoal, bool]:
    goal = get_or_create_daily_goal(session, user_id)
    goal.terms_count += 1
    completed_now = False

    if (
        goal.terms_count >= goal.target_terms
        and goal.quizzes_count >= goal.target_quizzes
        and not goal.bonus_collected
    ):
        goal.completed = True
        goal.bonus_collected = True
        completed_now = True

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal, completed_now


def record_daily_quiz(session: Session, user_id: str) -> Tuple[DailyGoal, bool]:
    goal = get_or_create_daily_goal(session, user_id)
    goal.quizzes_count += 1
    completed_now = False

    if (
        goal.terms_count >= goal.target_terms
        and goal.quizzes_count >= goal.target_quizzes
        and not goal.bonus_collected
    ):
        goal.completed = True
        goal.bonus_collected = True
        completed_now = True

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal, completed_now


def check_and_unlock_badges(session: Session, user_id: str) -> List[Badge]:
    """
    Evaluates milestone criteria and awards newly earned badges.
    """
    user = session.get(UserProfile, user_id)
    if not user:
        return []

    # Get already unlocked badge keys
    existing = session.exec(select(Badge.badge_key).where(Badge.user_id == user_id)).all()
    unlocked_keys = set(existing)
    newly_unlocked = []

    # 1. First spark: >= 1 explanation
    if "first_spark" not in unlocked_keys:
        count = len(session.exec(select(HistoryItem).where(HistoryItem.user_id == user_id)).all())
        if count >= 1:
            b = Badge(user_id=user_id, badge_key="first_spark", name="First Spark", description="Explained your first AI term!", icon="⚡")
            session.add(b)
            newly_unlocked.append(b)

    # 2. Bookworm: >= 5 glossary explanations
    if "glossary_worm" not in unlocked_keys:
        glossary_count = len(session.exec(select(HistoryItem).where(HistoryItem.user_id == user_id, HistoryItem.from_glossary == True)).all())
        if glossary_count >= 5:
            b = Badge(user_id=user_id, badge_key="glossary_worm", name="Bookworm", description="Learned 5 terms from the official glossary!", icon="📚")
            session.add(b)
            newly_unlocked.append(b)

    # 3. Quiz scholar: >= 3 quizzes completed
    if "quiz_scholar" not in unlocked_keys:
        quizzes = len(session.exec(select(QuizGradeRecord).where(QuizGradeRecord.user_id == user_id)).all())
        if quizzes >= 3:
            b = Badge(user_id=user_id, badge_key="quiz_scholar", name="Scholar", description="Completed 3 AI knowledge quizzes!", icon="🎓")
            session.add(b)
            newly_unlocked.append(b)

    # 4. Flame keeper: streak >= 3
    if "flame_keeper" not in unlocked_keys and user.streak_count >= 3:
        b = Badge(user_id=user_id, badge_key="flame_keeper", name="Flame Keeper", description="Maintained a 3-day learning streak!", icon="🔥")
        session.add(b)
        newly_unlocked.append(b)

    # 5. Neural cadet: level >= 3
    if "neural_cadet" not in unlocked_keys and user.level >= 3:
        b = Badge(user_id=user_id, badge_key="neural_cadet", name="Neural Cadet", description="Reached Level 3!", icon="🤖")
        session.add(b)
        newly_unlocked.append(b)

    if newly_unlocked:
        session.commit()

    return newly_unlocked


def get_user_stats(session: Session, user_id: str = "student_1") -> UserStatsResponse:
    user = get_or_create_user(session, user_id)
    lvl, title, in_level, high, pct = calculate_level(user.xp)
    goal = get_or_create_daily_goal(session, user_id)

    # Fetch badges
    unlocked_badges = {b.badge_key: b for b in session.exec(select(Badge).where(Badge.user_id == user_id)).all()}
    badge_items = []
    for meta in ALL_AVAILABLE_BADGES:
        k = meta["key"]
        is_unlocked = k in unlocked_badges
        unlocked_dt = unlocked_badges[k].unlocked_at if is_unlocked else None
        badge_items.append(
            BadgeItem(
                badge_key=k,
                name=meta["name"],
                description=meta["description"],
                icon=meta["icon"],
                unlocked=is_unlocked,
                unlocked_at=unlocked_dt,
            )
        )

    return UserStatsResponse(
        id=user.id,
        name=user.name,
        xp=user.xp,
        level=lvl,
        level_title=title,
        xp_in_level=in_level,
        xp_for_next_level=high,
        progress_percent=pct,
        streak_count=user.streak_count,
        streak_freezes=user.streak_freezes,
        credits=user.credits,
        daily_goal={
            "date": goal.date_str,
            "terms_count": goal.terms_count,
            "target_terms": goal.target_terms,
            "quizzes_count": goal.quizzes_count,
            "target_quizzes": goal.target_quizzes,
            "completed": goal.completed,
            "bonus_collected": goal.bonus_collected,
        },
        badges=badge_items,
    )
