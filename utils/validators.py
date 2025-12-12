"""
Input Validators

Validation functions for user inputs.
"""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an email address.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return True, None  # Email is optional

    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, None


def validate_slug(slug: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL slug.

    Args:
        slug: Slug to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not slug:
        return False, "Slug is required"

    # Slug should be lowercase, alphanumeric, and hyphens only
    pattern = r'^[a-z0-9-]+$'

    if not re.match(pattern, slug):
        return False, "Slug must contain only lowercase letters, numbers, and hyphens"

    if slug.startswith('-') or slug.endswith('-'):
        return False, "Slug cannot start or end with a hyphen"

    if '--' in slug:
        return False, "Slug cannot contain consecutive hyphens"

    return True, None


def validate_transcript(transcript: str, max_length: int = 100000) -> Tuple[bool, Optional[str]]:
    """
    Validate a transcript.

    Args:
        transcript: Transcript text
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not transcript:
        return False, "Transcript cannot be empty"

    if len(transcript.strip()) < 50:
        return False, "Transcript is too short (minimum 50 characters)"

    if len(transcript) > max_length:
        return False, f"Transcript is too long (maximum {max_length:,} characters)"

    return True, None


def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a name (member, program, group, etc).

    Args:
        name: Name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"

    name = name.strip()

    if len(name) < 2:
        return False, "Name must be at least 2 characters"

    if len(name) > 255:
        return False, "Name is too long (maximum 255 characters)"

    # Check for at least some alphanumeric characters
    if not re.search(r'[a-zA-Z0-9]', name):
        return False, "Name must contain at least one letter or number"

    return True, None


def validate_date_range(start_date, end_date) -> Tuple[bool, Optional[str]]:
    """
    Validate a date range.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Tuple of (is_valid, error_message)
    """
    if start_date and end_date:
        if end_date < start_date:
            return False, "End date must be after start date"

    return True, None


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input by trimming and removing excess whitespace.

    Args:
        text: Input text
        max_length: Optional maximum length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Trim whitespace
    text = text.strip()

    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)

    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text


def generate_slug_from_name(name: str) -> str:
    """
    Generate a URL-friendly slug from a name.

    Args:
        name: Name to convert

    Returns:
        Slug string
    """
    # Convert to lowercase
    slug = name.lower()

    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')

    # Remove non-alphanumeric characters (except hyphens)
    slug = re.sub(r'[^a-z0-9-]', '', slug)

    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug


def validate_member_role(role: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a group member role.

    Args:
        role: Role string

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_roles = ['facilitator', 'participant', 'observer']

    if role not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"

    return True, None


def validate_attendance_status(status: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an attendance status.

    Args:
        status: Status string

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_statuses = [
        'present',
        'absent_without_updates',
        'travelling',
        'family_time',
        'work_business',
        'wellness'
    ]

    if status not in valid_statuses:
        return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

    return True, None
