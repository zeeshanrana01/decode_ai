import json
from typing import Optional
from sqlmodel import Session, select

from app.models.db import QuizGradeRecord, Badge, UserProfile
from app.models.schemas import QuizGradeResult
from app.services.gamification import (
    get_or_create_user,
    add_xp,
    record_daily_quiz,
    check_and_unlock_badges,
    DAILY_GOAL_BONUS_XP,
)
from app.agent.prompts import SYSTEM_QUIZ_GRADER
from app.config import OLLAMA_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY


def heuristic_grade(term: str, question: str, user_answer: str) -> tuple[int, str]:
    """
    Fast, reliable heuristic grader for school students when LLM is unavailable or offline.
    """
    clean_answer = user_answer.strip().lower()
    clean_term = term.strip().lower()

    # Empty or too short
    if len(clean_answer) < 3 or clean_answer in ["no", "idk", "i don't know", "skip", "none"]:
        return 0, "Don't worry! AI concepts take time to learn. Take another look at the mental model and try again!"

    # Multiple choice check (A, B, C)
    if len(clean_answer) <= 3 and any(choice in clean_answer for choice in ["a", "b", "c"]):
        # Look for option keywords in question
        if "b)" in question.lower() and "b" in clean_answer:
            return 3, "Spot on! That's exactly right. Great job picking the correct concept!"
        elif "a)" in question.lower() and "a" in clean_answer:
            return 3, "Super job! You nailed the question!"
        else:
            return 1, "Good guess! Review the 3 steps above to see why another option fits best."

    # Freeform keywords matching
    tokens = clean_answer.split()
    term_words = [w for w in clean_term.split() if len(w) > 3]

    relevance_count = sum(1 for w in tokens if len(w) > 4)
    has_term_keyword = any(kw in clean_answer for kw in term_words)

    if relevance_count >= 5 or (relevance_count >= 3 and has_term_keyword):
        return 3, f"Fantastic explanation! You explained how {term} works clearly in your own words. Super proud of your understanding!"
    elif relevance_count >= 2:
        return 2, f"Great effort! You've got the general idea of {term}. Keep refining how the steps connect!"
    elif relevance_count >= 1:
        return 1, f"You are on the right track! Try adding one more detail about what {term} actually does in real life."
    else:
        return 0, f"Nice attempt! Remember: {term} focuses on helping AI learn or retrieve information safely. Review the analogy and try once more!"


def grade_quiz(
    term: str,
    question: str,
    user_answer: str,
    user_id: str,
    session: Session,
) -> QuizGradeResult:
    """
    Evaluates student quiz answer, awards XP, records stats, and triggers gamification events.
    """
    user = get_or_create_user(session, user_id)
    score: int = 1
    feedback: str = ""

    # Attempt LLM grading if available
    graded_by_llm = False
    if OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
            prompt = (
                f"{SYSTEM_QUIZ_GRADER}\n\n"
                f"Term: {term}\n"
                f"Quiz Question: {question}\n"
                f"Student Answer: {user_answer}\n\n"
                f"Return JSON strictly formatted: {{\"score\": <0-3>, \"feedback\": \"<friendly feedback>\"}}"
            )
            resp = llm.invoke(prompt)
            data = json.loads(resp.content.strip("```json").strip("```").strip())
            score = int(data.get("score", 1))
            feedback = str(data.get("feedback", ""))
            graded_by_llm = True
        except Exception:
            pass

    if not graded_by_llm:
        score, feedback = heuristic_grade(term, question, user_answer)

    # Calculate XP
    xp_map = {0: 5, 1: 15, 2: 30, 3: 50}
    xp_to_award = xp_map.get(score, 10)

    # Reward credits for good answers
    if score >= 2:
        user.credits = min(user.credits + 1, 30)

    # Save grade record
    record = QuizGradeRecord(
        user_id=user_id,
        term=term,
        quiz_question=question,
        user_answer=user_answer,
        score=score,
        feedback=feedback,
        xp_awarded=xp_to_award,
    )
    session.add(record)
    session.commit()

    # Update daily goal
    goal, goal_completed_now = record_daily_quiz(session, user_id)
    if goal_completed_now:
        xp_to_award += DAILY_GOAL_BONUS_XP
        feedback += f" 🌟 Daily Goal Achieved! +{DAILY_GOAL_BONUS_XP} Bonus XP!"

    # Add XP & level check
    leveled_up, new_lvl, new_title = add_xp(session, user, xp_to_award)

    # Check for newly unlocked badges
    unlocked_badge_name = None
    if score == 3:
        # Check quiz_wiz badge
        wiz_badge = session.exec(
            select(Badge).where(Badge.user_id == user_id, Badge.badge_key == "quiz_wiz")
        ).first()
        if not wiz_badge:
            wiz = Badge(
                user_id=user_id,
                badge_key="quiz_wiz",
                name="Quiz Wiz",
                description="Scored a perfect 3/3 on an AI quiz!",
                icon="🎯",
            )
            session.add(wiz)
            session.commit()
            unlocked_badge_name = "Quiz Wiz 🎯"

    # Evaluate any other milestone badges
    milestone_badges = check_and_unlock_badges(session, user_id)
    if milestone_badges and not unlocked_badge_name:
        unlocked_badge_name = f"{milestone_badges[0].name} {milestone_badges[0].icon}"

    return QuizGradeResult(
        score=score,
        feedback=feedback,
        xp_awarded=xp_to_award,
        badge_unlocked=unlocked_badge_name,
        streak_bonus=False,
        new_level=new_lvl if leveled_up else None,
    )
