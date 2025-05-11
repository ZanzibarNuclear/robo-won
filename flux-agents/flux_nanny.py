from time import sleep
from datetime import datetime
import requests


class Nanny():
    def __init__(self):
        self._action = None
        self.cnt = 0
        self.api_url = "http://localhost:3030/api/about"  # Example REST endpoint
        self.last_fetch = datetime.now()
        self.events = {}

    def do_action(self):
        print(f"Request #{self.cnt}")

        try:
            # Make the REST API call
            response = requests.get(self.api_url)
            # Check if the request was successful
            if response.status_code == 200:
                # Parse and print the JSON payload
                payload = response.json()
                print("Response payload:")
                print(payload)

                latestEvent = payload['latestEvent'][0]
                key = latestEvent['id']
                print(latestEvent, key)

                if key in self.events:
                    print("We have this one.")
                else:
                    self.events[key] = latestEvent
                    print("Captured the new event.")

            else:
                print(f"Error: Received status code {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

        self.cnt = self.cnt + 1
        print('===')
        sleep(5)


def main():
    roboNanny = Nanny()
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
