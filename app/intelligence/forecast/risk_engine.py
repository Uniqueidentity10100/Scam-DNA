

STAGE_WEIGHTS = {
    "RECON": 5,
    "TRUST": 10,
    "BAIT": 25,
    "PRESSURE": 40,
    "EXTRACTION": 60
}

DNA_WEIGHTS = {
    "URG": 25,
    "PAY": 35,
    "LINK": 20,
    "AUTH": 10,
    "FEAR": 20,
    "REW": 15
}

def _parse_dna(dna_code: str):
    if not dna_code:
        return []
    return [p.strip() for p in dna_code.split("-")]

def calculate_risk(dna_code, stage, similarity_score=0.0, mutation_level="Original"):
    """
    Returns:
        dict: {
            score: int (0-100),
            label: str,
            explanation: list[str]
        }
    """

    score = 0
    explanation = []

    # 1. DNA-based scoring
    dna_parts = _parse_dna(dna_code)
    for part in dna_parts:
        weight = DNA_WEIGHTS.get(part, 0)
        score += weight
        if weight > 0:
            explanation.append(f"Detected {part} signal (+{weight})")

    # 2. Behavioral stage scoring
    stage_weight = STAGE_WEIGHTS.get(stage, 0)
    score += stage_weight
    if stage_weight > 0:
        explanation.append(f"Message is in {stage} stage (+{stage_weight})")

    # 3. Similarity-based boost
    if similarity_score >= 0.85:
        score += 25
        explanation.append("Highly similar to known scam family (+25)")
    elif similarity_score >= 0.65:
        score += 15
        explanation.append("Moderately similar to known scam family (+15)")
    elif similarity_score >= 0.45:
        score += 5
        explanation.append("Low similarity to known scam patterns (+5)")

    # 4. Mutation factor
    if mutation_level == "Minor":
        score += 5
        explanation.append("Minor mutation detected (+5)")
    elif mutation_level == "Major":
        score += 15
        explanation.append("Major mutation detected (+15)")

    # Clamp score
    score = min(100, max(0, score))

    # 5. Risk Label
    if score >= 80:
        label = "CRITICAL"
    elif score >= 60:
        label = "HIGH"
    elif score >= 30:
        label = "MEDIUM"
    else:
        label = "LOW"

    return {
        "score": score,
        "label": label,
        "explanation": explanation
    }
