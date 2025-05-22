from config.settings import WON_SERVICE_ENDPOINT, WON_SERVICE_API_KEY
import requests
from urllib.parse import urlencode
from utils.logger import logger, log_connection_error


class FluxService:

    def __init__(self):
        self.endpoint = WON_SERVICE_ENDPOINT
        self.headers = {
            "Authorization": f"Bearer {WON_SERVICE_API_KEY}"
        }
        logger.info("flux_api_initialized", endpoint=self.endpoint)

    def fetch_last_rating(self):
        logger.info("fetching_last_rating", message="See where we left off")
        url = f"{self.endpoint}/flux-moderation/latest-ratings?limit=1"
        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error("fetch_last_rating_failed",
                             status_code=response.status_code, response=str(response))
                raise Exception(
                    "Blocked from getting latest; something may be misconfigured")
        except requests.exceptions.ConnectionError as e:
            log_connection_error(logger, "fetch_last_rating_connection_error",
                                 url=url, message="Connection error while fetching last rating")
            raise Exception(
                "Connection error while fetching last rating") from e

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

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error("fetch_next_fluxes_failed",
                             status_code=response.status_code)
                return None
        except requests.exceptions.ConnectionError as e:
            log_connection_error(logger, "fetch_next_fluxes_connection_error",
                                 url=url, message="Connection error while fetching fluxes")
            return None

    def rate_flux(self, flux_id, rating_code, reason):
        url = f"{self.endpoint}/flux-moderation/ratings"
        payload = {
            "fluxId": flux_id,
            "rating": rating_code,
            "reason": reason
        }
        try:
            logger.info("storing_flux_rating", flux_id=flux_id)
            response = requests.post(
                url=url,
                json=payload,
                headers=self.headers
            )
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                logger.error("rate_flux_failed",
                             status_code=response.status_code, flux_id=flux_id)
                return None
        except requests.exceptions.ConnectionError as e:
            log_connection_error(logger, "rate_flux_connection_error",
                                 url=url, flux_id=flux_id,
                                 message="Connection error while rating flux")
            return None
        except Exception as e:
            logger.exception("rate_flux_exception",
                             error=str(e), flux_id=flux_id)
            return None
