from bots.flux_nanny import FluxNanny
from time import sleep
from config.settings import POLLING_INTERVAL


def main():
    print("=== STARTING AGENTS ===")
    roboNanny = FluxNanny()
    polling_rest = 60
    if POLLING_INTERVAL:
        polling_rest = int(POLLING_INTERVAL)
    round = 0
    while True:
        try:
            round += 1
            print(f"==== ROUND {round} ====")
            roboNanny.do_action()
            print(f"==== END ROUND {round} ====\n")
            print(f"==== chill for {polling_rest} seconds ====\n")
            sleep(polling_rest)
        except KeyboardInterrupt as e:
            print("I guess you have had enough. Shutting down...goodbye!")
            break
        except Exception as e:
            print("Well, that was unexpected. Gotta go.", e)
            break


if __name__ == "__main__":
    main()
