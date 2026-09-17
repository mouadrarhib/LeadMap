def calculate_lead_score(lead: dict | object, opportunity_score: int | None = None) -> int:
    def get(name: str, default=None):
        return lead.get(name, default) if isinstance(lead, dict) else getattr(lead, name, default)

    score = 0
    score += 25 if get("email") else 0
    score += 15 if get("phone") else 0
    score += 15 if get("website") else 0
    score += 15 if get("rating") is not None else 0
    score += 10 if (get("review_count", 0) or 0) > 5 else 0
    opportunity = opportunity_score if opportunity_score is not None else get("opportunity_score", 20)
    score += max(0, min(int(opportunity or 0), 20))
    return min(score, 100)

