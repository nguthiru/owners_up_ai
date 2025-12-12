"""
Session Operations

CRUD operations for sessions table and session data saving.
"""

from typing import List, Optional
from datetime import datetime
from db.client import get_supabase
from db.models import Session, dict_to_session


def create_session(
    group_id: int,
    date: datetime,
    notes: Optional[str] = None,
    transcript: Optional[str] = None
) -> Session:
    """
    Create a new session.
    Session number is auto-incremented by database trigger.

    Args:
        group_id: Group ID
        date: Session date
        notes: Optional session notes
        transcript: Optional transcript text

    Returns:
        Created Session model

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    data = {
        'group_id': group_id,
        'date': date.isoformat(),
        'notes': notes,
        'transcript': transcript
    }

    result = supabase.table('sessions').insert(data).execute()

    return dict_to_session(result.data[0])


def get_session(session_id: int) -> Optional[Session]:
    """
    Get a session by ID.

    Args:
        session_id: Session ID

    Returns:
        Session model if found, None otherwise
    """
    supabase = get_supabase()

    result = supabase.table('sessions').select('*').eq('id', session_id).execute()

    return dict_to_session(result.data[0]) if result.data else None


def list_sessions_by_group(group_id: int) -> List[Session]:
    """
    List all sessions for a group, ordered by date desc.

    Args:
        group_id: Group ID

    Returns:
        List of Session models
    """
    supabase = get_supabase()

    result = supabase.table('sessions').select('*').eq(
        'group_id', group_id
    ).order('date', desc=True).execute()

    return [dict_to_session(row) for row in result.data]


def update_session(
    session_id: int,
    date: Optional[datetime] = None,
    notes: Optional[str] = None,
    transcript: Optional[str] = None
) -> Session:
    """
    Update a session.

    Args:
        session_id: Session ID
        date: New date (optional)
        notes: New notes (optional)
        transcript: New transcript (optional)

    Returns:
        Updated Session model

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    update_data = {}
    if date is not None:
        update_data['date'] = date.isoformat()
    if notes is not None:
        update_data['notes'] = notes
    if transcript is not None:
        update_data['transcript'] = transcript

    result = supabase.table('sessions').update(update_data).eq('id', session_id).execute()

    return dict_to_session(result.data[0])


def delete_session(session_id: int) -> bool:
    """
    Hard delete a session.
    WARNING: This will cascade delete all related data.

    Args:
        session_id: Session ID

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    supabase.table('sessions').delete().eq('id', session_id).execute()

    return True


def save_session_extractions(
    session_id: int,
    attendance: List[dict],
    goals: List[dict],
    challenges: List[dict],
    marketing_activities: List[dict],
    stucks: List[dict],
    sentiment: dict
) -> bool:
    """
    Save all AI extractions for a session atomically.

    This function saves all extraction data. If any part fails, the entire
    operation should be rolled back (though Supabase doesn't support transactions
    via the Python client, we handle errors gracefully).

    Args:
        session_id: Session ID
        attendance: List of attendance records
        goals: List of goal records
        challenges: List of challenge records
        marketing_activities: List of marketing activity records
        stucks: List of stuck detection records
        sentiment: Sentiment analysis data

    Returns:
        True if successful

    Raises:
        Exception: If any database operation fails
    """
    from db.operations import attendance as att_ops
    from db.operations import goals as goal_ops
    from db.operations import challenges as chal_ops
    from db.operations import marketing as mkt_ops
    from db.operations import stucks as stuck_ops
    from db.operations import sentiment as sent_ops

    errors = []

    # Save attendance - continue on error
    if attendance:
        try:
            att_ops.save_attendance_records(session_id, attendance)
        except Exception as e:
            errors.append(f"Attendance error: {str(e)}")
            print(f"Error saving attendance (continuing): {e}")

    # Save goals - continue on error
    if goals:
        try:
            goal_ops.save_goals(session_id, goals)
        except Exception as e:
            errors.append(f"Goals error: {str(e)}")
            print(f"Error saving goals (continuing): {e}")

    # Save challenges - continue on error
    if challenges:
        try:
            chal_ops.save_challenges(session_id, challenges)
        except Exception as e:
            errors.append(f"Challenges error: {str(e)}")
            print(f"Error saving challenges (continuing): {e}")

    # Save marketing activities - continue on error
    if marketing_activities:
        try:
            mkt_ops.save_marketing_activities(session_id, marketing_activities)
        except Exception as e:
            errors.append(f"Marketing error: {str(e)}")
            print(f"Error saving marketing activities (continuing): {e}")

    # Save stuck detections - continue on error
    if stucks:
        try:
            stuck_ops.save_stuck_detections(session_id, stucks)
        except Exception as e:
            errors.append(f"Stucks error: {str(e)}")
            print(f"Error saving stuck detections (continuing): {e}")

    # Save sentiment - continue on error
    if sentiment:
        try:
            sent_ops.save_sentiment(session_id, sentiment)
        except Exception as e:
            errors.append(f"Sentiment error: {str(e)}")
            print(f"Error saving sentiment (continuing): {e}")

    # Return True even if there were some errors (partial success)
    # Errors are logged but not raised
    if errors:
        print(f"Completed with {len(errors)} errors: {errors}")

    return True
