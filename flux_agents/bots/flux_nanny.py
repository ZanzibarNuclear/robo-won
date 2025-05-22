from datetime import datetime
from urllib.parse import urlencode
from models.llm import ModeratorBotClient
from api.flux_svc import FluxService
from utils.logger import logger


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
            logger.error("ai_not_responsive",
                         message="No response from AI agent")
            raise Exception("AI agent is not responsive")

        # set high-water mark to prevent re-work
        results = self.flux_svc.fetch_last_rating()
        if results:
            latest = results[0]
            time_posted = datetime.fromisoformat(latest['postedAt'])
            formatted_time = time_posted.strftime("%Y-%m-%d %H:%M:%S")
            logger.info("high_water_mark_set", timestamp=formatted_time)
            self.latest_flux_seen = time_posted

    def do_action(self):
        offset = 0
        check_for_more = True

        while check_for_more:
            logger.info("checking_new_items",
                        message="Anything new to process?")
            if self.latest_flux_seen:
                batch = self.flux_svc.fetch_next_fluxes(
                    posted_after=self.latest_flux_seen)
            else:
                batch = self.flux_svc.fetch_next_fluxes(offset=offset)

            # returning None is the signal for an error that got swallowed
            if not batch:
                logger.error("batch_processing_failed",
                             message="Some kind of failure happened. Exiting...")
                return

            total = batch["total"]
            if (total):
                logger.info("new_flux_posts_found", count=total)
            else:
                logger.info("no_new_items")
                break

            items = batch["items"]
            for flux in items:
                key = flux["id"]

                # avoid reprocessing fluxes, since using AI is relatively expensive
                if key in self.fluxes_seen:
                    logger.info("flux_already_processed", flux_id=key)
                else:
                    # rate the flux post
                    logger.info("rating_flux", flux_id=key)
                    (rating, reason) = self.ai.evaluate_post(flux)
                    logger.info("flux_rated", flux_id=key,
                                rating=rating, reason=reason)

                    # record the rating
                    self.flux_svc.rate_flux(key, rating, reason)

                    # remember that we processed it (until restart, at least)
                    self.fluxes_seen[key] = rating
                    if (flux["postedAt"]):
                        self.latest_flux_seen = datetime.fromisoformat(
                            flux["postedAt"])

            offset += total
            check_for_more = batch["hasMore"]

        logger.info("processing_complete", message="That's all for now.")
