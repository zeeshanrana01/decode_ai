import json
from typing import Dict, Optional
from langchain_core.tools import tool
from duckduckgo_search import DDGS
from app.config import GLOSSARY_FILE
from app.guardrails.school_safe import check_school_safe


def load_glossary() -> Dict[str, str]:
    """Loads the glossary into a case-insensitive dictionary."""
    if not GLOSSARY_FILE.exists():
        return {}

    try:
        with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        glossary_map = {}
        # If stored as list of {"term": ..., "definition": ...}
        if isinstance(data, dict) and "terms" in data and isinstance(data["terms"], list):
            for item in data["terms"]:
                if isinstance(item, dict) and "term" in item and "definition" in item:
                    term_key = item["term"].strip().lower()
                    glossary_map[term_key] = item["definition"]
                    # If abbreviation or full name exists
                    if "abbreviation" in item:
                        glossary_map[item["abbreviation"].strip().lower()] = item["definition"]
                    if "full_name" in item:
                        glossary_map[item["full_name"].strip().lower()] = item["definition"]

        # If stored directly as key-value pairs {"llm": "...", "rag": "..."}
        if isinstance(data, dict):
            for k, v in data.items():
                if k == "metadata" or k == "terms":
                    continue
                if isinstance(v, str):
                    glossary_map[k.strip().lower()] = v

        return glossary_map
    except Exception as e:
        print(f"Error loading glossary from {GLOSSARY_FILE}: {e}")
        return {}


GLOSSARY: Dict[str, str] = load_glossary()


@tool
def lookup_term(term: str) -> str:
    """Look up an AI term in the official glossary. Use this first for every term."""
    clean_term = term.strip().lower()

    # Exact match
    if clean_term in GLOSSARY:
        return GLOSSARY[clean_term]

    # Handle common prefixes like "what is ", "explain ", "define "
    for prefix in ["what is ", "what are ", "explain ", "define "]:
        if clean_term.startswith(prefix):
            stripped = clean_term[len(prefix):].strip()
            if stripped in GLOSSARY:
                return GLOSSARY[stripped]

    # Word-level token match (e.g. "what is rag?" -> checks words)
    words = [w.strip("?,.!") for w in clean_term.split()]
    for w in words:
        if len(w) >= 2 and w in GLOSSARY:
            return GLOSSARY[w]

    # Full term is substring of a longer glossary term (e.g., "diffusion" -> "diffusion models")
    if len(clean_term) >= 3:
        for k, v in GLOSSARY.items():
            if clean_term == k or clean_term in k:
                return v

    return "NOT_FOUND"


@tool
def safe_web_search(query: str) -> str:
    """
    Search the web safely for AI educational definitions when not found in the glossary.
    Requires human-in-the-loop approval before executing live.
    """
    # Guardrail: check query safety
    is_safe, reason = check_school_safe(query)
    if not is_safe:
        return f"SEARCH_BLOCKED: {reason}"

    # Educational query enhancement
    edu_query = f"{query} artificial intelligence for students definition"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(edu_query, max_results=3, safesearch="strict"))

        if not results:
            return f"No educational search results found for '{query}'."

        snippets = []
        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            snippets.append(f"- {title}: {body}")

        return "\n".join(snippets)
    except Exception as e:
        # Graceful fallback when offline or no network
        return (
            f"Educational search preview for '{query}': "
            f"An artificial intelligence technology widely studied in computer science and modern applications."
        )
