"""
Configuration parameters for Flux Agents
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

WON_SERVICE_ENDPOINT = os.getenv("WON_SERVICE_ENDPOINT")
WON_SERVICE_API_KEY = os.getenv("WON_SERVICE_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
LLM_MODEL = os.getenv("LLM_MODEL")

POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "60"))  # seconds
LOG_FILE = os.getenv("LOG_FILE", "./flux-moderator.log")
PID_FILE = os.getenv("PID_FILE", "./flux-moderator.pid")
