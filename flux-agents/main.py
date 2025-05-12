from bots.flux_nanny import FluxNanny
from config import settings


def main():
    roboNanny = FluxNanny()

    print("Service endpoint:", settings.WON_SERVICE_ENDPOINT)

    while True:
        try:
            roboNanny.do_action()
        except KeyboardInterrupt as e:
            print("I guess you have had enough. Shutting down...goodbye!")
            break
        except Exception as e:
            print("Well, that was unexpected. Gotta go.", e)
            break


if __name__ == "__main__":
    main()
