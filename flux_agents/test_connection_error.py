import requests
from utils.logger import logger, log_connection_error
import json


def test_connection_error_handling():
    """Test the connection error handling functionality."""
    print("Testing connection error handling...")

    # Test the log_connection_error function
    try:
        # Attempt to connect to a non-existent server to trigger a ConnectionError
        requests.get("http://non-existent-server.example", timeout=1)
    except requests.exceptions.ConnectionError as e:
        # Log the connection error
        log_connection_error(logger, "test_connection_error",
                             url="http://non-existent-server.example",
                             message="This is a test connection error")
        print("Successfully caught and logged a connection error")

    # Test the connection_error_processor
    try:
        # Attempt to connect to a non-existent server to trigger a ConnectionError
        requests.get("http://another-non-existent-server.example", timeout=1)
    except requests.exceptions.ConnectionError as e:
        # Log the exception with the logger
        logger.exception("test_processor_connection_error",
                         url="http://another-non-existent-server.example",
                         message="Testing the connection error processor")
        print("Successfully tested the connection error processor")


if __name__ == "__main__":
    test_connection_error_handling()
