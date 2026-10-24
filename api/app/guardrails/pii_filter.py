import re
from typing import Tuple, List

# Email pattern
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Phone numbers (US/International format variations)
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")

# Social Security Numbers (SSN) / National Identification
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

# Credit Card numbers (13-19 digits, space or hyphen separated)
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")

# Student / ID card numbers (e.g. ID: 12345678 or Student #987654)
STUDENT_ID_REGEX = re.compile(r"\b(?:student\s*(?:id|#)?\s*[:=]?\s*\d{5,10})\b", re.IGNORECASE)


def mask_pii(text: str) -> Tuple[str, bool, List[str]]:
    """
    Detects and masks Personally Identifiable Information (PII) to protect student privacy.
    Returns (masked_text, pii_detected, list_of_detected_types).
    """
    if not text:
        return text, False, []

    detected_types = []
    sanitized = text

    if EMAIL_REGEX.search(sanitized):
        sanitized = EMAIL_REGEX.sub("[REDACTED_EMAIL]", sanitized)
        detected_types.append("email")

    if SSN_REGEX.search(sanitized):
        sanitized = SSN_REGEX.sub("[REDACTED_SSN]", sanitized)
        detected_types.append("ssn")

    if CREDIT_CARD_REGEX.search(sanitized):
        sanitized = CREDIT_CARD_REGEX.sub("[REDACTED_CREDIT_CARD]", sanitized)
        detected_types.append("credit_card")

    if PHONE_REGEX.search(sanitized):
        sanitized = PHONE_REGEX.sub("[REDACTED_PHONE]", sanitized)
        detected_types.append("phone")

    if STUDENT_ID_REGEX.search(sanitized):
        sanitized = STUDENT_ID_REGEX.sub("[REDACTED_STUDENT_ID]", sanitized)
        detected_types.append("student_id")

    return sanitized, len(detected_types) > 0, detected_types
