"""
Application Constants

Constant values used throughout the application.
"""

# Name Matching
MATCH_THRESHOLD = 80  # Minimum confidence score (0-100) for automatic name matching

# Transcript Processing
MAX_TRANSCRIPT_LENGTH = 100000  # Maximum characters in a transcript
MIN_TRANSCRIPT_LENGTH = 50  # Minimum characters in a transcript

# Risk Rating
RISK_WINDOW_WEEKS = 2  # Number of weeks to look back for risk assessment

# Session Configuration
DEFAULT_SESSION_NOTES = ""

# Attendance Statuses
ATTENDANCE_STATUSES = [
    "present",
    "absent_without_updates",
    "travelling",
    "family_time",
    "work_business",
    "wellness"
]

# Group Member Roles
GROUP_MEMBER_ROLES = [
    "facilitator",
    "participant",
    "observer"
]

# Marketing Activity Stages
MARKETING_STAGES = [
    "none_mentioned",
    "meetings",
    "proposals",
    "closed"
]

# Marketing Activity Types
MARKETING_TYPES = [
    "none_mentioned",
    "network_activation",
    "linkedin",
    "cold_outreach"
]

# Marketing Contract Types
CONTRACT_TYPES = [
    "one_time",
    "monthly",
    "hybrid"
]

# Risk Rating Categories
RISK_CATEGORIES = [
    "high_risk",
    "medium_risk",
    "on_track",
    "intervention",
    "crushing_it"
]

# UI Configuration
ITEMS_PER_PAGE = 20  # Default pagination
MAX_DISPLAY_NAME_LENGTH = 50  # Truncate long names in tables

# Sentiment Score Range
MIN_SENTIMENT_SCORE = 1
MAX_SENTIMENT_SCORE = 5

# Colors for UI (can be used in Streamlit)
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_ERROR = "#F44336"
COLOR_INFO = "#2196F3"
COLOR_NEUTRAL = "#9E9E9E"

# Status Badge Colors
STATUS_COLORS = {
    "present": COLOR_SUCCESS,
    "absent_without_updates": COLOR_ERROR,
    "travelling": COLOR_INFO,
    "family_time": COLOR_INFO,
    "work_business": COLOR_WARNING,
    "wellness": COLOR_INFO
}

# Risk Rating Colors
RISK_COLORS = {
    "high_risk": COLOR_ERROR,
    "medium_risk": COLOR_WARNING,
    "on_track": COLOR_SUCCESS,
    "intervention": COLOR_WARNING,
    "crushing_it": "#9C27B0"  # Purple for crushing it
}
