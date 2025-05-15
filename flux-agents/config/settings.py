"""
Configuration parameters for Flux Agents
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

WON_SERVICE_ENDPOINT = os.getenv("WON_SERVICE_ENDPOINT")
OLLAMA_HOST = os.getenv["OLLAMA_HOST"]
