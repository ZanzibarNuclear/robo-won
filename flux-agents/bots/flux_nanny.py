from config import settings
from datetime import datetime
from time import sleep
import requests
from urllib.parse import urlencode


class FluxNanny:
    """Looks at every flux, and flags objectionable or questionable content."""

    def __init__(self):
        self._action = None
        self.cnt = 0
        self.fluxes_seen = {}
        self.last_fetch = None
        self.high_water_mark = None

    def fetch_fluxes(self):
        check_for_more = True
        offset = 0
        limit = 1
        try:
            while check_for_more:
                queryParams = urlencode({"offset": offset, "limit": limit})
                flux_url = "{}/fluxes?{}".format(
                    settings.WON_SERVICE_ENDPOINT, queryParams)
                print("Ask for new flux:", flux_url)
                response = requests.get(flux_url)
                self.last_fetch = datetime.now()

                # Check if the request was successful
                if response.status_code == 200:
                    payload = response.json()
                    items = payload["items"]
                    total = payload["total"]
                    has_more = payload["hasMore"]

                    print("Response payload:")
                    print(payload)

                    for flux in items:
                        key = flux["id"]

                        if key in self.fluxes_seen:
                            print("Already got it")
                        else:
                            print("Processing flux id=", key)
                            print(flux["content"])
                            self.fluxes_seen[key] = flux
                            self.high_water_mark = flux["posted_at"]

                    offset = offset + total
                    check_for_more = has_more

                else:
                    print(
                        f"Error: Received status code {response.status_code}")
                    check_for_more = False

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

    def do_action(self):
        print(f"Request #{self.cnt}")
        self.fetch_fluxes()

        self.cnt = self.cnt + 1
        print('===')
        sleep(5)
