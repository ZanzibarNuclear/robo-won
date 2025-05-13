from bots.flux_nanny import FluxNanny
from config import settings
from time import sleep


def main():
    roboNanny = FluxNanny()
    round = 0
    print("Service endpoint:", settings.WON_SERVICE_ENDPOINT)

    while True:
        try:
            round += 1
            print("==== KICK OFF BOTS ====")
            roboNanny.do_action()
            print("\nFinished round {}\n\n\n".format(round))
            sleep(10)
        except KeyboardInterrupt as e:
            print("I guess you have had enough. Shutting down...goodbye!")
            break
        except Exception as e:
            print("Well, that was unexpected. Gotta go.", e)
            break


if __name__ == "__main__":
    main()
