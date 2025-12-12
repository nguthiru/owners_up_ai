"""
Supabase Client Singleton

Provides a single, reusable instance of the Supabase client throughout the application.
"""

from supabase import create_client, Client
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Global client instance
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """
    Get or create Supabase client singleton.

    Returns:
        Client: Supabase client instance

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are not set
    """
    global _supabase_client

    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables. "
                "Please check your .env file."
            )

        _supabase_client = create_client(url, key)

    return _supabase_client


def reset_client():
    """
    Reset the Supabase client singleton.
    Useful for testing or when credentials change.
    """
    global _supabase_client
    _supabase_client = None
