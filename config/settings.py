"""
Application Settings

Centralized configuration management using environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Application Configuration
APP_NAME = "OwnersUp Platform"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Validation
def validate_settings():
    """
    Validate that all required settings are present.

    Raises:
        ValueError: If any required setting is missing
    """
    required_settings = {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY,
        "GOOGLE_API_KEY": GOOGLE_API_KEY
    }

    missing = [key for key, value in required_settings.items() if not value]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please check your .env file."
        )


# Run validation on import (optional - comment out if you want manual validation)
# validate_settings()
