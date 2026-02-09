"""Application configuration - loads from .env file."""

import os
from dotenv import load_dotenv

load_dotenv()

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# Session
SECRET_KEY = os.getenv("SECRET_KEY", "physicsoj-dev-secret-change-in-production")

# Server
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
