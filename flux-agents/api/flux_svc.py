from config.settings import WON_SERVICE_ENDPOINT, WON_SERVICE_API_KEY
import requests
from urllib.parse import urlencode


class FluxService:

    def __init__(self):
        self.endpoint = WON_SERVICE_ENDPOINT
        self.headers = {
            "Authorization": f"Bearer {WON_SERVICE_API_KEY}"
        }
        print(f"Flux API at: {self.endpoint}")

    def fetch_last_rating(self):
        print("See where we left off")
        url = f"{self.endpoint}/flux-moderation/latest-ratings?limit=1"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response}")
            raise Exception(
                "Blocked from getting latest; something may be misconfigured")

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
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Error: Received status code {response.status_code}")
            return None

    def rate_flux(self, flux_id, rating_code, reason):
        url = f"{self.endpoint}/flux-moderation/ratings"
        payload = {
            "fluxId": flux_id,
            "rating": rating_code,
            "reason": reason
        }
        post_headers = self.headers.copy()
        post_headers['Content-Type'] = 'application/json'

        try:
            print("Rate a flux", payload)
            response = requests.post(
                url=url,
                json=payload,
            )
            print(f"Request method used: {response.request.method}")
            print(f"Request URL: {response.request.url}")
            print(f"Request headers: {response.request.headers}")

            if response.status_code == 200:
                print("Something is fishy; should have created a new record")
                return response.json()
            elif response.status_code == 201:
                print("Rated", response)
                return response.json()
            else:
                print(f"Error: Received status code {response.status_code}")
                return None
        except Exception as e:
            print("Trouble sending rating to WoN service.", e)
