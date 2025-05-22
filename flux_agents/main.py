from bots.flux_nanny import FluxNanny
from time import sleep
from config.settings import POLLING_INTERVAL
from utils.logger import logger


def main():
    logger.info("starting_agents", message="=== STARTING AGENTS ===")
    roboNanny = FluxNanny()
    polling_rest = 60
    if POLLING_INTERVAL:
        polling_rest = int(POLLING_INTERVAL)
    round = 0
    while True:
        try:
            round += 1
            logger.info("round_start", round=round)
            roboNanny.do_action()
            logger.info("round_end", round=round)
            logger.info("polling_rest", seconds=polling_rest)
            sleep(polling_rest)
        except KeyboardInterrupt:
            logger.info("shutdown", reason="keyboard_interrupt",
                        message="I guess you have had enough. Shutting down...goodbye!")
            break
        except Exception as e:
            logger.exception("unexpected_error", error=str(
                e), message="Well, that was unexpected. Gotta go.")
            break


if __name__ == "__main__":
    main()
