from datetime import datetime
from urllib.parse import urlencode
from models.llm import ModeratorBotClient
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

        # make sure AI is alive and well
        if not self.ai.ping_ai():
            print("No response from AI agent")
            raise Exception("AI agent is not responsive")

        # set high-water mark to prevent re-work
        results = self.flux_svc.fetch_last_rating()
        if results:
            latest = results[0]
            time_posted = datetime.fromisoformat(latest['postedAt'])
            print(
                f"Setting high water mark at: {time_posted.strftime("%Y-%m-%d %H:%M:%S")}\n")
            self.latest_flux_seen = time_posted

    def do_action(self):
        offset = 0
        check_for_more = True

        while check_for_more:
            print("Anything new to process?")
            if self.latest_flux_seen:
                batch = self.flux_svc.fetch_next_fluxes(
                    posted_after=self.latest_flux_seen)
            else:
                batch = self.flux_svc.fetch_next_fluxes(offset=offset)

            # returning None is the signal for an error that got swallowed
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
                        f"AI has rated this flux as '{rating}' because '{reason}'")

                    # record the rating
                    self.flux_svc.rate_flux(key, rating, reason)

                    # remember that we processed it (until restart, at least)
                    self.fluxes_seen[key] = rating
                    if (flux["postedAt"]):
                        self.latest_flux_seen = datetime.fromisoformat(
                            flux["postedAt"])

            offset += total
            check_for_more = batch["hasMore"]

        print("That's all for now.")
