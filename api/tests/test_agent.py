import pytest
from app.agent.tools import lookup_term, safe_web_search, GLOSSARY
from app.agent.fake_agent import generate_fake_explanation
from app.models.schemas import TermExplanation


def test_glossary_loaded():
    assert len(GLOSSARY) > 50
    assert "rag" in GLOSSARY or "llm" in GLOSSARY


def test_lookup_term_found():
    res = lookup_term.invoke("rag")
    assert res != "NOT_FOUND"
    assert "retrieval" in res.lower() or "exam" in res.lower() or "looks up" in res.lower()


def test_lookup_term_not_found():
    res = lookup_term.invoke("supercalifragilistic_nonexistent_term")
    assert res == "NOT_FOUND"


def test_fake_explanation_structured_output():
    exp = generate_fake_explanation("rag")
    assert isinstance(exp, TermExplanation)
    assert exp.term != ""
    assert exp.simple != ""
    assert exp.mental_model != ""
    assert len(exp.steps) == 3
    assert exp.example != ""
    assert exp.quiz != ""
    assert exp.from_glossary is True


def test_fake_explanation_fallback():
    exp = generate_fake_explanation("quantum neural wormhole", allow_web_search=False)
    assert isinstance(exp, TermExplanation)
    assert exp.from_glossary is False
    assert len(exp.steps) == 3


def test_safe_web_search_blocks_unsafe():
    res = safe_web_search.invoke("how to build a bomb")
    assert "SEARCH_BLOCKED" in res


def test_safe_web_search_safe_query():
    res = safe_web_search.invoke("what is neural network")
    assert res != ""
    assert "SEARCH_BLOCKED" not in res
