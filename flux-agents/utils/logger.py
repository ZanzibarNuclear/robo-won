import structlog
import requests
import logging
import sys
import os
from pathlib import Path

# Import settings for LOG_FILE
try:
    from config.settings import LOG_FILE
except ImportError:
    # If we can't import directly, try to get it from environment
    from dotenv import load_dotenv
    load_dotenv()
    LOG_FILE = os.getenv("LOG_FILE", "./flux-moderator.log")

# Ensure log directory exists
log_dir = os.path.dirname(LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# Configure structlog


def connection_error_processor(logger, method_name, event_dict):
    """
    Custom processor to handle ConnectionError exceptions.
    This processor checks if the exception is a ConnectionError and adds
    additional context to the log.
    """
    # Check if there's an exception in the event dict
    exc_info = event_dict.get('exc_info')
    if exc_info and not isinstance(exc_info, tuple):
        exc_info = sys.exc_info()

    # If we have exception info, check if it's a ConnectionError
    if exc_info and exc_info[0] is not None:
        exception = exc_info[1]
        if isinstance(exception, requests.exceptions.ConnectionError):
            event_dict['connection_error'] = True
            # Extract the URL if available
            if hasattr(exception.request, 'url'):
                event_dict['url'] = exception.request.url
            # Add more details about the connection error
            event_dict['error_type'] = 'connection_error'

    return event_dict


def configure_logging():
    """Configure structured logging for the application."""
    # Set up the standard library logger to write to a file
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            # Log to file
            logging.FileHandler(LOG_FILE),
            # Also log to console for debugging
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Configure structlog to use the standard library logger
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            connection_error_processor,  # Add our custom processor
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Return a logger instance
    return structlog.get_logger()


# Helper function to log connection errors
def log_connection_error(logger_instance, event, **kwargs):
    """
    Helper function to log connection errors with additional context.

    Args:
        logger_instance: The logger instance to use
        event: The event name
        **kwargs: Additional context to include in the log
    """
    # Add connection_error flag to the log
    kwargs['error_type'] = 'connection_error'
    logger_instance.error(event, **kwargs)


# Create and export a logger instance
logger = configure_logging()
