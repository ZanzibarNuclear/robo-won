import requests
import sys
import os
import importlib.util
import time

# Import the logger directly from the file
spec = importlib.util.spec_from_file_location("logger",
                                              "/Users/dave/projects/na/won/platform/robo-won/flux-agents/utils/logger.py")
logger_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_module)
logger = logger_module.logger
LOG_FILE = logger_module.LOG_FILE

print(f"Logs will be written to: {LOG_FILE}")


def test_connection_error_logging():
    """Test the connection error logging functionality."""
    print("Testing connection error logging...")

    try:
        print("Attempting to connect to non-existent server...")
        # Manually create a ConnectionError to test our logging
        # This is more reliable than trying to trigger a real network error
        raise requests.exceptions.ConnectionError(
            requests.Request(
                method='GET', url='http://non-existent-server.example').prepare(),
            "Simulated connection error for testing"
        )
    except requests.exceptions.ConnectionError as e:
        # Log the connection error
        print(f"ConnectionError caught: {str(e)}")
        logger.error("Failed to connect to server", exc_info=True)
        print("ConnectionError logged. Check the log output below:")

        # Give the logger a moment to write to the file
        time.sleep(0.5)

        # Check if the log file exists and display its contents
        if os.path.exists(LOG_FILE):
            print(f"\nContents of log file ({LOG_FILE}):")
            with open(LOG_FILE, 'r') as f:
                log_contents = f.read()
                print(log_contents)
        else:
            print(f"Log file not found at: {LOG_FILE}")
    except Exception as e:
        print(f"Caught a different exception: {type(e).__name__}")
        logger.error("Unexpected error", exc_info=True)


if __name__ == "__main__":
    test_connection_error_logging()
