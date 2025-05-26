from datetime import datetime
from urllib.parse import urlencode
from models.llm import ModeratorBotClient
from api.flux_svc import FluxService
from utils.logger import logger


class FluxNanny:
    """Looks at every flux that needs a rating. Asks AI for the rating, and updates the Flux Service."""

    def __init__(self):
        self.flux_svc = FluxService()
        self.ai = ModeratorBotClient()

        # make sure AI is alive and well
        if not self.ai.ping_ai():
            logger.error("ai_not_responsive",
                         message="No response from AI agent")
            raise Exception("AI agent is not responsive")

    def do_action(self):
        check_for_more = True

        logger.info("processing_started", message="Processing new fluxes.")
        while check_for_more:
            # gets the next batch of unrated fluxes
            batch = self.flux_svc.fetch_next_fluxes()

            # returning None is the signal for an error that got swallowed
            if not batch:
                logger.error("processing_failed",
                             message="Some kind of failure happened. Exiting...")
                return

            # total = batch["total"]
            # if (total):
            #     logger.info("new_flux_posts_found", total=total)
            # else:
            #     logger.info("no_new_items")
            #     break

            items = batch["items"]
            for flux in items:
                key = flux["id"]

                # rate the flux post
                logger.info("rating_flux", flux_id=key)
                (rating, reason) = self.ai.evaluate_post(flux)

                # record the rating
                self.flux_svc.rate_flux(key, rating, reason)

            check_for_more = batch["hasMore"]

        logger.info("processing_complete", message="That's all for now.")
