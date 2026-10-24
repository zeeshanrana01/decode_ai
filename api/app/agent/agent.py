import os
import json
from typing import Optional, Dict, Any
from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.agent.tools import lookup_term, safe_web_search, GLOSSARY
from app.agent.prompts import SYSTEM_EXPLAINER
from app.agent.fake_agent import generate_fake_explanation
from app.models.schemas import TermExplanation
from app.config import OLLAMA_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY


def get_llm():
    """
    Returns an active chat model:
    1. If OPENAI_API_KEY is present -> ChatOpenAI
    2. If OLLAMA is reachable -> ChatOllama
    3. Fallback -> FakeListChatModel for zero-crash offline execution
    """
    if OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        except Exception:
            pass

    # Try Ollama
    try:
        from langchain_ollama import ChatOllama
        ollama_model = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.3,
        )
        return ollama_model
    except Exception:
        pass

    # Safe deterministic fake model fallback
    dummy_json = json.dumps({
        "term": "RAG",
        "simple": "RAG lets an AI look up reliable information before giving an answer.",
        "mental_model": "RAG is like an open-book exam for computers.",
        "steps": [
            "1. You ask a question.",
            "2. The AI searches its textbook files.",
            "3. It uses what it read to write a clear answer."
        ],
        "example": "A student handbook bot checking the dress code rules.",
        "quiz": "Why does RAG check reference documents first? A) To ensure accuracy, B) To guess randomly, C) To shut down.",
        "from_glossary": True,
        "used_web_search": False,
    })
    return FakeListChatModel(responses=[dummy_json])


# Build modern LangChain agent
try:
    llm = get_llm()
    agent = create_agent(
        model=llm,
        tools=[lookup_term, safe_web_search],
        system_prompt=SYSTEM_EXPLAINER,
        response_format=TermExplanation,
    )
except Exception as e:
    print(f"Warning: Could not create standard LangChain agent directly: {e}. Using deterministic agent.")
    agent = None


def explain_term(term: str, allow_web_search: bool = False) -> TermExplanation:
    """
    Core function to explain an AI term for students.
    Runs via create_agent or deterministic fallback.
    """
    # If agent is initialized with a live LLM, attempt invoke
    if agent and not isinstance(llm, FakeListChatModel):
        try:
            result = agent.invoke({
                "messages": [{"role": "user", "content": f"Explain the AI term: {term}"}]
            })
            if "structured_response" in result and isinstance(result["structured_response"], TermExplanation):
                return result["structured_response"]
        except Exception as e:
            print(f"LLM invoke failed, falling back to student explainer: {e}")

    # Deterministic high-quality offline student explainer
    return generate_fake_explanation(term=term, allow_web_search=allow_web_search)
