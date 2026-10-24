import json
import asyncio
import uuid
from typing import AsyncGenerator
from sqlmodel import Session

from app.guardrails import (
    check_school_safe,
    mask_pii,
    check_prompt_injection,
    rate_limiter,
    tool_call_limiter,
)
from app.agent.tools import lookup_term
from app.agent.agent import explain_term
from app.models.db import HistoryItem, HITLRequest
from app.models.schemas import TermExplanation
from app.services.gamification import (
    get_or_create_user,
    add_xp,
    record_daily_term,
    check_and_unlock_badges,
    get_user_stats,
    DAILY_GOAL_BONUS_XP,
)


def default_serializer(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


def format_sse(event: str, data: dict) -> str:
    """Encodes a payload as a standard SSE event."""
    return f"event: {event}\ndata: {json.dumps(data, default=default_serializer)}\n\n"


async def generate_explanation_stream(
    term: str,
    user_id: str,
    allow_web_search: bool,
    client_ip: str,
    session: Session,
) -> AsyncGenerator[str, None]:
    """
    Asynchronously streams the explanation generation pipeline via Server-Sent Events (SSE).
    """
    session_id = str(uuid.uuid4())

    # 1. Rate limit verification
    is_allowed, remaining = rate_limiter.is_allowed(client_ip or user_id)
    if not is_allowed:
        yield format_sse("error", {
            "type": "rate_limited",
            "message": "Too many requests. Please wait a moment before asking again!"
        })
        return

    # 2. Guardrails: School safety
    is_safe, safety_reason = check_school_safe(term)
    if not is_safe:
        yield format_sse("error", {
            "type": "school_safe_violation",
            "message": f"School Safety Alert: {safety_reason} Please ask an AI-related topic!"
        })
        return

    # 3. Guardrails: Prompt injection
    is_injection_free, pattern = check_prompt_injection(term)
    if not is_injection_free:
        yield format_sse("error", {
            "type": "prompt_injection_blocked",
            "message": f"Nice try! Prompt injection attempt detected ('{pattern}'). Please ask genuine AI questions."
        })
        return

    # 4. Guardrails: PII detection and redaction
    clean_term, pii_detected, pii_types = mask_pii(term)
    if pii_detected:
        yield format_sse("status", {
            "step": "pii_redacted",
            "message": f"Student Privacy: Masked sensitive information ({', '.join(pii_types)}) for your safety."
        })
        await asyncio.sleep(0.1)

    # 5. Credits check
    user = get_or_create_user(session, user_id)
    if user.credits < 1:
        yield format_sse("error", {
            "type": "credits_exhausted",
            "message": "You are out of daily energy credits (0/20)! Answer quizzes or return tomorrow to refresh."
        })
        return

    # Deduct 1 credit for term exploration
    user.credits -= 1
    session.add(user)
    session.commit()

    # Step: Announce start
    yield format_sse("status", {
        "step": "guardrails_passed",
        "message": "Guardrails passed: School-safe, PII protected, injection-free."
    })
    await asyncio.sleep(0.15)

    # Step: Tool limit tracking
    tool_call_limiter.record_call(session_id)

    # Step: Glossary check
    yield format_sse("status", {
        "step": "glossary_lookup",
        "message": f"Agent executing lookup_term('{clean_term}') against Stanford HAI glossary..."
    })
    await asyncio.sleep(0.2)

    definition = lookup_term.invoke(clean_term)

    if definition != "NOT_FOUND":
        yield format_sse("thought", {
            "step": "glossary_found",
            "message": "Found official definition! Structuring school mental model and 3 steps..."
        })
        await asyncio.sleep(0.2)
    else:
        yield format_sse("thought", {
            "step": "glossary_miss",
            "message": "Term not in standard glossary."
        })
        await asyncio.sleep(0.1)

        # If web search is not allowed, check if we should trigger HITL approval or use AI knowledge
        if not allow_web_search:
            # Create a pending HITL request
            hitl_id = f"hitl_{uuid.uuid4().hex[:8]}"
            req = HITLRequest(
                id=hitl_id,
                user_id=user_id,
                action="safe_web_search",
                query=clean_term,
                reason="Term was not found in the official glossary. Would you like to allow safe web search?",
                status="pending",
            )
            session.add(req)
            session.commit()

            yield format_sse("hitl_prompt", {
                "request_id": hitl_id,
                "tool": "safe_web_search",
                "query": clean_term,
                "message": f"'{clean_term}' wasn't found in the glossary. Allow DecodeAI to perform a safe educational web search?"
            })
            await asyncio.sleep(0.15)
        else:
            yield format_sse("thought", {
                "step": "web_search_active",
                "message": f"Executing safe_web_search for '{clean_term}' with school safety filter..."
            })
            await asyncio.sleep(0.2)

    # 6. Generate the structured explanation
    yield format_sse("status", {
        "step": "synthesizing",
        "message": "Crafting everyday analogy, 3 steps, real-life example, and interactive quiz..."
    })
    await asyncio.sleep(0.2)

    explanation: TermExplanation = explain_term(clean_term, allow_web_search=allow_web_search)

    # Send final structured explanation
    yield format_sse("explanation", explanation.model_dump())
    await asyncio.sleep(0.1)

    # 7. Update Gamification: XP, Streaks, Daily Goals, Badges, History
    xp_to_award = 20
    goal, goal_completed_now = record_daily_term(session, user_id)
    if goal_completed_now:
        xp_to_award += DAILY_GOAL_BONUS_XP

    leveled_up, new_lvl, new_title = add_xp(session, user, xp_to_award)

    # Save to history
    history = HistoryItem(
        user_id=user_id,
        term=explanation.term,
        simple=explanation.simple,
        mental_model=explanation.mental_model,
        steps_json=json.dumps(explanation.steps),
        example=explanation.example,
        quiz=explanation.quiz,
        from_glossary=explanation.from_glossary,
        used_web_search=explanation.used_web_search,
    )
    session.add(history)
    session.commit()

    # Check and award badges
    new_badges = check_and_unlock_badges(session, user_id)
    badge_name = f"{new_badges[0].name} {new_badges[0].icon}" if new_badges else None

    # Get updated stats
    stats = get_user_stats(session, user_id)

    yield format_sse("gamification", {
        "xp_gained": xp_to_award,
        "daily_goal_completed": goal_completed_now,
        "leveled_up": leveled_up,
        "new_level": new_lvl if leveled_up else None,
        "new_title": new_title if leveled_up else None,
        "badge_unlocked": badge_name,
        "stats": stats.model_dump(),
    })

    # 8. Complete stream
    yield format_sse("done", {"status": "complete"})
