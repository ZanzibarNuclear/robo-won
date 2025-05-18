from config.settings import WON_SERVICE_ENDPOINT
import requests
from urllib.parse import urlencode


class FluxService:

    def __init__(self):
        print(f"Flux service at endpoint: {WON_SERVICE_ENDPOINT}")
        self.endpoint = WON_SERVICE_ENDPOINT

    def fetch_next_fluxes(self, offset=0, limit=5, posted_after=None):
        filters = {"order": "oldest"}
        if offset:
            filters["offset"] = str(offset)
        if limit:
            filters["limit"] = str(limit)
        if posted_after:
            filters["after"] = posted_after
        queryParams = urlencode(filters)

        url = f"{self.endpoint}/fluxes?{queryParams}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Error: Received status code {response.status_code}")
            return None

    def rate_flux(self, flux_id, rating_code, reason):
        url = f"{self.endpoint}/flux-moderation/ratings"
        payload = {
            "flux_id": flux_id,
            "rating_code": rating_code,
            "reason": reason
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
