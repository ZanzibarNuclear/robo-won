from datetime import datetime
from urllib.parse import urlencode
from api.llm import ModeratorBotClient
from api.flux_svc import FluxService


class FluxNanny:
    """Looks at every flux, and flags objectionable or questionable content."""

    def __init__(self):
        self._action = None
        self.fluxes_seen = {}
        self.last_fetch = None
        self.latest_flux_seen = None
        self.flux_svc = FluxService()
        self.ai = ModeratorBotClient()

        if self.ai.ping_ai():
            print("AI agent is reachable")
        else:
            print("No response from AI agent")
            raise Exception("AI agent is not responsive")

    def do_action(self):
        offset = 0
        check_for_more = True
        while check_for_more:
            print("Anything new to process?")
            batch = self.flux_svc.fetch_next_fluxes()
            if not batch:
                print("some kind of failure happened. exiting...")
                return

            total = batch["total"]
            if (total):
                print("Found some new flux posts.")
            else:
                print("No new items.")
                break

            items = batch["items"]
            for flux in items:
                key = flux["id"]

                # avoid reprocessing fluxes, since using AI is relatively expensive
                if key in self.fluxes_seen:
                    print("Already processed flux with ID", key)
                else:
                    # rate the flux post
                    print("Asking AI to rate flux", key)
                    (rating, reason) = self.ai.evaluate_post(flux)
                    print(
                        "AI has rated this flux as '{rating}' because '{reason}'")

                    # record the rating
                    self.flux_svc.rate_flux(key, rating, reason)

                    # remember that we processed it (until restart, at least)
                    self.fluxes_seen[key] = rating
                    if (flux["postedAt"]):
                        self.latest_flux_seen = datetime.fromisoformat(
                            flux["postedAt"])

            offset += total
            check_for_more = batch["hasMore"]

        print("That's all for now. Check as often as you like for anything new.\n\n")
