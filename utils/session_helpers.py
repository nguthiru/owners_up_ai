"""
Session Helper Functions

Utility functions for session-related operations.
"""

from datetime import datetime, date
from typing import Optional


def format_session_date(session_date: datetime) -> str:
    """
    Format a session date for display.

    Args:
        session_date: Session datetime

    Returns:
        Formatted date string (e.g., "Mon, Jan 15, 2024")
    """
    return session_date.strftime("%a, %b %d, %Y")


def format_session_display_name(session_number: int, session_date: datetime) -> str:
    """
    Create a display name for a session.

    Args:
        session_number: Session number
        session_date: Session date

    Returns:
        Display name (e.g., "Session 5 - Jan 15, 2024")
    """
    date_str = session_date.strftime("%b %d, %Y")
    return f"Session {session_number} - {date_str}"


def parse_session_date(date_input) -> datetime:
    """
    Parse various date inputs to datetime.

    Args:
        date_input: Can be datetime, date, or string

    Returns:
        datetime object

    Raises:
        ValueError: If date cannot be parsed
    """
    if isinstance(date_input, datetime):
        return date_input
    elif isinstance(date_input, date):
        return datetime.combine(date_input, datetime.min.time())
    elif isinstance(date_input, str):
        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y",
            "%d/%m/%Y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_input, fmt)
            except ValueError:
                continue
        raise ValueError(f"Could not parse date: {date_input}")
    else:
        raise ValueError(f"Invalid date type: {type(date_input)}")


def calculate_session_duration(transcript: str) -> Optional[int]:
    """
    Estimate session duration based on transcript length.
    Very rough estimate: ~150 words per minute.

    Args:
        transcript: Session transcript

    Returns:
        Estimated duration in minutes, or None if cannot estimate
    """
    if not transcript:
        return None

    word_count = len(transcript.split())
    estimated_minutes = word_count / 150

    return int(estimated_minutes) if estimated_minutes > 0 else None


def get_session_summary_stats(session_data: dict) -> dict:
    """
    Generate summary statistics for a session.

    Args:
        session_data: Dict containing session extractions

    Returns:
        Dict with summary stats:
        {
            'total_attendance': int,
            'present_count': int,
            'absent_count': int,
            'goals_count': int,
            'challenges_count': int,
            'stucks_count': int,
            'has_sentiment': bool
        }
    """
    attendance = session_data.get('attendance', [])
    goals = session_data.get('goals', [])
    challenges = session_data.get('challenges', [])
    stucks = session_data.get('stucks', [])
    sentiment = session_data.get('sentiment')

    present_count = sum(1 for a in attendance if a.get('status') == 'present')

    return {
        'total_attendance': len(attendance),
        'present_count': present_count,
        'absent_count': len(attendance) - present_count,
        'goals_count': len(goals),
        'challenges_count': len(challenges),
        'stucks_count': len(stucks),
        'has_sentiment': sentiment is not None
    }


def validate_session_extractions(session_data: dict) -> tuple[bool, list[str]]:
    """
    Validate that session extraction data is complete.

    Args:
        session_data: Dict containing session extractions

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Check for required keys
    required_keys = ['attendance', 'goals', 'challenges', 'marketing_activities', 'stucks', 'sentiment']
    for key in required_keys:
        if key not in session_data:
            errors.append(f"Missing required key: {key}")

    # Check that at least some data exists
    if session_data.get('attendance') and len(session_data['attendance']) == 0:
        errors.append("No attendance records found")

    # Check that attendance records have required fields
    for idx, att in enumerate(session_data.get('attendance', [])):
        if 'matched_member_id' not in att:
            errors.append(f"Attendance record {idx} missing member ID")
        if 'status' not in att:
            errors.append(f"Attendance record {idx} missing status")

    # Check goals
    for idx, goal in enumerate(session_data.get('goals', [])):
        if 'matched_member_id' not in goal:
            errors.append(f"Goal {idx} missing member ID")
        if 'goal' not in goal or not goal['goal']:
            errors.append(f"Goal {idx} missing goal text")

    return (len(errors) == 0, errors)


def group_extractions_by_member(session_data: dict) -> dict:
    """
    Group all session extractions by member for easy viewing.

    Args:
        session_data: Dict containing session extractions

    Returns:
        Dict mapping member_id -> {attendance, goals, challenges, marketing, stucks}
    """
    member_data = {}

    # Group attendance
    for att in session_data.get('attendance', []):
        member_id = att.get('matched_member_id')
        if member_id:
            if member_id not in member_data:
                member_data[member_id] = {
                    'attendance': None,
                    'goals': [],
                    'challenges': [],
                    'marketing': [],
                    'stucks': []
                }
            member_data[member_id]['attendance'] = att

    # Group goals
    for goal in session_data.get('goals', []):
        member_id = goal.get('matched_member_id')
        if member_id and member_id in member_data:
            member_data[member_id]['goals'].append(goal)

    # Group challenges
    for challenge in session_data.get('challenges', []):
        member_id = challenge.get('matched_member_id')
        if member_id and member_id in member_data:
            member_data[member_id]['challenges'].append(challenge)

    # Group marketing
    for activity in session_data.get('marketing_activities', []):
        member_id = activity.get('matched_member_id')
        if member_id and member_id in member_data:
            member_data[member_id]['marketing'].append(activity)

    # Group stucks
    for stuck in session_data.get('stucks', []):
        member_id = stuck.get('matched_member_id')
        if member_id and member_id in member_data:
            member_data[member_id]['stucks'].append(stuck)

    return member_data
