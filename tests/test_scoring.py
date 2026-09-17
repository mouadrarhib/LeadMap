from services.lead_scoring import calculate_lead_score


def test_complete_lead_scores_100() -> None:
    lead = {
        "email": "hi@company.ma", "phone": "123", "website": "https://company.ma",
        "rating": 4.6, "review_count": 10, "opportunity_score": 20,
    }
    assert calculate_lead_score(lead) == 100


def test_opportunity_score_is_capped() -> None:
    assert calculate_lead_score({}, opportunity_score=99) == 20

