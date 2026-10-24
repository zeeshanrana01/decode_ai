import os
from pathlib import Path

# Paths
APP_DIR = Path(__file__).resolve().parent
API_DIR = APP_DIR.parent
ROOT_DIR = API_DIR.parent

# Find glossary file in candidate locations
CANDIDATE_GLOSSARY_PATHS = [
    API_DIR / "data" / "glossary.json",
    ROOT_DIR / "data" / "glossary.json",
    API_DIR / "glossary.json",
]

GLOSSARY_FILE = next((p for p in CANDIDATE_GLOSSARY_PATHS if p.exists()), CANDIDATE_GLOSSARY_PATHS[0])

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{API_DIR / 'decode_ai.db'}")

# Model Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:0.8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Guardrails and Limits
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "3"))
DEFAULT_DAILY_CREDITS = int(os.getenv("DEFAULT_DAILY_CREDITS", "20"))
DEFAULT_STREAK_FREEZES = int(os.getenv("DEFAULT_STREAK_FREEZES", "2"))
DAILY_GOAL_TERMS = int(os.getenv("DAILY_GOAL_TERMS", "3"))
DAILY_GOAL_QUIZZES = int(os.getenv("DAILY_GOAL_QUIZZES", "1"))
DAILY_GOAL_BONUS_XP = 50
