import re
from typing import Tuple, Optional

# Known prompt injection & jailbreak indicators
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?prior\s+instructions",
    r"system\s*prompt",
    r"reveal\s+(your\s+)?(instructions|prompt|rules)",
    r"print\s+(your\s+)?(instructions|system\s+message)",
    r"dan\s+mode",
    r"do\s+anything\s+now",
    r"act\s+as\s+(an?\s+)?unrestricted",
    r"jailbreak",
    r"bypass\s+safety",
    r"disable\s+guardrails",
    r"<\|im_start\|>",
    r"\[INST\]",
    r"roleplay\s+as\s+an\s+evil",
]

COMPILED_INJECTIONS = [re.compile(pat, re.IGNORECASE) for pat in INJECTION_PATTERNS]


def check_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if the user input contains prompt injection, jailbreaking, or system prompt probing.
    Returns (is_safe, detected_pattern_name).
    """
    if not text:
        return True, None

    lower_text = text.lower()
    for pattern in COMPILED_INJECTIONS:
        match = pattern.search(lower_text)
        if match:
            return False, match.group(0)

    return True, None
