import re

SPAM_KEYWORDS = [
    "verify", "urgent", "immediately", "click", "limited",
    "win", "bonus", "free", "suspended", "blocked",
    "investment", "crypto", "password", "bank",
    "payment", "transfer", "call now"
]

LINK_PATTERN = re.compile(r"(http|https|www\.)", re.IGNORECASE)
MONEY_PATTERN = re.compile(r"(₹|\$|usd|rs|payment|transfer)", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\b\d{10,}\b")

def spam_score(text: str):
    score = 0
    reasons = []

    lower = text.lower()

    # Keyword signals
    for word in SPAM_KEYWORDS:
        if word in lower:
            score += 10
            reasons.append(f"Contains keyword '{word}' (+10)")

    # Structural signals
    if LINK_PATTERN.search(text):
        score += 25
        reasons.append("Contains link (+25)")

    if MONEY_PATTERN.search(text):
        score += 20
        reasons.append("Contains money-related request (+20)")

    if PHONE_PATTERN.search(text):
        score += 10
        reasons.append("Contains direct contact number (+10)")

    return score, reasons

def classify_message(text: str, threshold=30):
    """
    Returns:
    {
        label: "SPAM" | "NOT_SPAM",
        score: int,
        explanation: list[str]
    }
    """
    score, reasons = spam_score(text)

    if score >= threshold:
        return {
            "label": "SPAM",
            "score": score,
            "explanation": reasons
        }
    else:
        return {
            "label": "NOT_SPAM",
            "score": score,
            "explanation": reasons or ["No strong scam signals detected"]
        }