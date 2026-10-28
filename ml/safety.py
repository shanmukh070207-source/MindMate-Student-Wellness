"""Conservative safety check that runs BEFORE the classifier.

This is a simple phrase-matching check. It is deliberately separate from the
machine-learning model, and it is NOT a monitoring system: it cannot detect every
message that signals a crisis, and MindMate does not promise that it will.
Anyone in immediate danger should contact local emergency services.

Support contacts below were checked against public sources in October 2026
(Tele-MANAS: 14416 / 1-800-891-4416, run under India's National Tele Mental Health
Programme; 112 is India's national emergency number). Please re-verify them
before any real deployment, and change them if your users are outside India.
"""
import re

# Short phrases that suggest possible danger. Matching is intentionally broad
# (it is better to show a support message by mistake than to miss one).
_PATTERNS = [
    r"\bkill (myself|my self)\b",
    r"\bsuicid(e|al)\b",
    r"\bend (my|this) life\b",
    r"\bend it all\b",
    r"\bwant(ed)? to die\b",
    r"\bwish i (was|were) dead\b",
    r"\bdon'?t want to (live|be alive|be here)\b",
    r"\bno reason to live\b",
    r"\bbetter off (dead|without me)\b",
    r"\bhurt(ing)? myself\b",
    r"\bharm(ing)? myself\b",
    r"\bself[- ]?harm\b",
    r"\bcut(ting)? myself\b",
    r"\bnot want to wake up\b",
    r"\bcan'?t go on\b",
    r"\btake my own life\b",
    r"\boverdose\b",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]

SUPPORT_CONTACTS = [
    {
        "name": "Tele-MANAS (Government of India, 24x7, free)",
        "detail": "Call 14416 or 1-800-891-4416",
        "url": "https://telemanas.mohfw.gov.in",
    },
    {
        "name": "National emergency number (India)",
        "detail": "Call 112 if you or someone else is in immediate danger",
        "url": "",
    },
]

SAFETY_MESSAGE = (
    "I'm really sorry you're going through something this painful, and I'm glad you said it out loud. "
    "MindMate is only a simple wellness tool, so it can't give you the support you deserve right now. "
    "Please reach out to a person you trust, such as a friend, family member, hostel warden or college counsellor, "
    "and let them know how you feel. If you might be in immediate danger, please contact your local emergency "
    "services right away. If you are in India, you can call Tele-MANAS on 14416 or 1-800-891-4416, "
    "which is free and open 24 hours a day, or dial 112 in an emergency. "
    "If you are in another country, please contact your local emergency number or crisis line. "
    "You don't have to go through this alone."
)


def check_safety(text):
    """Return True if the text contains a phrase that may signal danger."""
    if not isinstance(text, str):
        return False
    cleaned = " ".join(text.split())
    return any(p.search(cleaned) for p in _COMPILED)


def safety_response():
    return {
        "category": "Safety",
        "message": SAFETY_MESSAGE,
        "contacts": SUPPORT_CONTACTS,
        "actions": [],
        "safety": True,
    }
