import re
from typing import Tuple, Optional

# Keywords and regex patterns strictly unsafe for school environments
UNSAFE_PATTERNS = [
    # Violence & weapons
    r"\b(bomb|explosive|weapon|gun|knife|stab|murder|assassinate|terrorist|terrorism)\b",
    # Self-harm & suicide
    r"\b(suicide|self-harm|kill\s+myself|cut\s+myself|end\s+my\s+life)\b",
    # Adult / explicit
    r"\b(porn|pornography|nude|sex|sexual|erotic|nsfw|xxx)\b",
    # Drugs & illicit substances
    r"\b(cocaine|heroin|meth|fentanyl|marijuana|weed|vape|narcotics)\b",
    # Malicious hacking & malware
    r"\b(ransomware|keylogger|ddos|exploit\s+vulnerability|steal\s+passwords)\b",
    # Vulgarity / hate speech (common samples)
    r"\b(fuck|shit|bitch|bastard|asshole|cunt|dick)\b",
]

COMPILED_UNSAFE = [re.compile(pat, re.IGNORECASE) for pat in UNSAFE_PATTERNS]


def check_school_safe(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that the input or output text is safe for a school learning environment.
    Returns (is_safe, failure_reason).
    """
    if not text or not text.strip():
        return True, None

    lower_text = text.lower()
    for pattern in COMPILED_UNSAFE:
        match = pattern.search(lower_text)
        if match:
            return False, f"Content contains topic inappropriate for school learners: '{match.group(0)}'."

    return True, None
