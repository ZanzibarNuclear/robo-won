from config import settings
from datetime import datetime
import requests
from urllib.parse import urlencode
from api.llm import ModeratorBotClient


class FluxNanny:
    """Looks at every flux, and flags objectionable or questionable content."""

    def __init__(self):
        self._action = None
        self.fluxes_seen = {}
        self.last_fetch = None
        self.high_water_mark = None
        self.ai = ModeratorBotClient()
        if self.ai.ping_ai():
            print("AI agent is reachable")
        else:
            print("No response from AI agent")
            raise Exception("AI agent is not responsive")

    def status_report(self):
        # print("The last time we checked for flux: {}\nThe latest flux we processed so far.\n".format(
        #     self.last_fetch, self.high_water_mark))
        print("""
            The last time we checked for flux: {}
            The latest flux we processed so far: {}
            We have processed {} fluxes since starting.
        """.format(datetime.isoformat(self.last_fetch), datetime.isoformat(self.high_water_mark), len(self.fluxes_seen)))

    def fetch_fluxes(self):
        check_for_more = True
        offset = 0
        limit = 10
        posted_after = None
        if self.high_water_mark:
            # Format with 'Z' for UTC timezone instead of '+00:00'
            posted_after = self.high_water_mark.strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ')

        try:
            while check_for_more:
                filter = {"order": "oldest"}
                if offset:
                    filter["offset"] = offset
                if limit:
                    filter["limit"] = limit
                if posted_after:
                    filter["after"] = posted_after
                queryParams = urlencode(filter)
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
                    print("\nFound {} fluxes to process.\n".format(total))

                    for flux in items:
                        key = flux["id"]

                        if key in self.fluxes_seen:
                            print("Already got it")
                        else:
                            print("Processing flux id=", key)
                            print(flux["content"])

                            rating = self.ai.evaluate_post(flux)
                            print(rating)
                            self.fluxes_seen[key] = rating

                            if (flux["postedAt"]):
                                self.high_water_mark = datetime.fromisoformat(
                                    flux["postedAt"])

                    offset = offset + total
                    check_for_more = has_more

                else:
                    print(
                        f"Error: Received status code {response.status_code}")
                    check_for_more = False

                self.status_report()
                if check_for_more:
                    print("But wait...there's more.")
                else:
                    print('===\n')

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

    def do_action(self):
        self.fetch_fluxes()
