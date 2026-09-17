from services.google_places import GooglePlacesService


def test_maps_google_place_payload() -> None:
    mapped = GooglePlacesService._map_place(
        {
            "id": "abc",
            "displayName": {"text": "Clinic"},
            "websiteUri": "https://clinic.ma",
            "rating": 4.5,
        },
        "Casablanca",
    )
    assert mapped["place_id"] == "abc"
    assert mapped["business_name"] == "Clinic"
    assert mapped["domain"] == "clinic.ma"
    assert "query_place_id=abc" in mapped["maps_url"]

