"""
Stuck Detections Operations

Operations for member_stucks table.
"""

from typing import List
from db.client import get_supabase


def save_stuck_detections(session_id: int, stucks: List[dict]) -> bool:
    """
    Save stuck detections for a session.

    Args:
        session_id: Session ID
        stucks: List of stuck detection dicts with structure:
            {
                'member_id': int,
                'classification': str,
                'stuck_summary': str,
                'exact_quotes': List[str],
                'potential_next_step': str (optional)
            }

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    # Prepare records for insertion
    records = []
    for stuck in stucks:
        records.append({
            'session_id': session_id,
            'member_id': stuck['member_id'],
            'classification': stuck['classification'],
            'stuck_summary': stuck['stuck_summary'],
            'exact_quotes': stuck.get('exact_quotes', []),
            'potential_next_step': stuck.get('potential_next_step')
        })

    if records:
        supabase.table('member_stucks').insert(records).execute()

    return True


def get_session_stucks(session_id: int) -> List[dict]:
    """
    Get all stuck detections for a session.

    Args:
        session_id: Session ID

    Returns:
        List of stuck detections with member info
    """
    supabase = get_supabase()

    result = supabase.table('member_stucks').select(
        '*, members(*)'
    ).eq('session_id', session_id).execute()

    return result.data


def get_member_stucks(member_id: int, limit: int = 10) -> List[dict]:
    """
    Get recent stuck detections for a member.

    Args:
        member_id: Member ID
        limit: Number of recent stucks to return

    Returns:
        List of stuck detections
    """
    supabase = get_supabase()

    result = supabase.table('member_stucks').select(
        '*, sessions(date, session_number)'
    ).eq('member_id', member_id).order('created_at', desc=True).limit(limit).execute()

    return result.data
