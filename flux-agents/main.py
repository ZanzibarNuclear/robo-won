from bots.flux_nanny import FluxNanny
from time import sleep
from config.settings import POLLING_INTERVAL


def main():
    roboNanny = FluxNanny()
    round = 0
    while True:
        try:
            round += 1
            print(f"==== ROUND {round} ====")
            roboNanny.do_action()
            print(f"\n==== END ROUND {round} ====\n\n")
            sleep(30)
        except KeyboardInterrupt as e:
            print("I guess you have had enough. Shutting down...goodbye!")
            break
        except Exception as e:
            print("Well, that was unexpected. Gotta go.", e)
            break


if __name__ == "__main__":
    main()
