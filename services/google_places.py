import logging
from typing import Any

import httpx

from utils.url_utils import domain_from_url

logger = logging.getLogger(__name__)


class PlacesError(RuntimeError):
    pass


class GooglePlacesService:
    endpoint = "https://places.googleapis.com/v1/places:searchText"
    fields = ",".join(
        [
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.nationalPhoneNumber",
            "places.websiteUri",
            "places.googleMapsUri",
            "places.primaryTypeDisplayName",
            "places.rating",
            "places.userRatingCount",
            "nextPageToken",
        ]
    )

    def __init__(self, api_key: str, timeout: int = 10):
        if not api_key:
            raise PlacesError("Add GOOGLE_MAPS_API_KEY to .env before searching.")
        self.api_key = api_key
        self.timeout = timeout

    def search(self, niche: str, location: str, max_results: int = 20) -> list[dict[str, Any]]:
        query = f"{niche} in {location}".strip()
        if not niche.strip() or not location.strip():
            raise PlacesError("Enter both a niche and a location.")
        max_results = max(1, min(max_results, 100))
        results: list[dict[str, Any]] = []
        page_token: str | None = None
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": self.fields,
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                while len(results) < max_results:
                    body: dict[str, Any] = {
                        "textQuery": query,
                        "pageSize": min(20, max_results - len(results)),
                    }
                    if page_token:
                        body["pageToken"] = page_token
                    response = client.post(self.endpoint, headers=headers, json=body)
                    if response.status_code == 429:
                        raise PlacesError("Google Places quota was exceeded. Check the API project quota.")
                    response.raise_for_status()
                    payload = response.json()
                    results.extend(self._map_place(place, location) for place in payload.get("places", []))
                    page_token = payload.get("nextPageToken")
                    if not page_token:
                        break
        except httpx.TimeoutException as exc:
            raise PlacesError("Google Places timed out. Try again.") from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:300]
            logger.warning("Places request failed: %s", exc.response.status_code)
            raise PlacesError(f"Google Places returned {exc.response.status_code}: {detail}") from exc
        return results[:max_results]

    @staticmethod
    def _map_place(place: dict[str, Any], city: str) -> dict[str, Any]:
        website = place.get("websiteUri")
        place_id = place.get("id")
        return {
            "place_id": place_id,
            "business_name": place.get("displayName", {}).get("text", "Unknown business"),
            "category": place.get("primaryTypeDisplayName", {}).get("text"),
            "address": place.get("formattedAddress"),
            "city": city,
            "phone": place.get("nationalPhoneNumber"),
            "website": website,
            "domain": domain_from_url(website),
            "maps_url": place.get("googleMapsUri")
            or (f"https://www.google.com/maps/search/?api=1&query_place_id={place_id}" if place_id else None),
            "rating": place.get("rating"),
            "review_count": place.get("userRatingCount", 0),
            "source": "GOOGLE_PLACES",
        }

