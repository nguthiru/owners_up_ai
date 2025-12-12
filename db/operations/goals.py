"""
Goals Operations

Operations for goals table.
"""

from typing import List
from db.client import get_supabase


def save_goals(session_id: int, goals: List[dict]) -> bool:
    """
    Save goals for a session.

    Args:
        session_id: Session ID
        goals: List of goal dicts with structure:
            {
                'member_id': int,
                'goal': str,
                'is_vague': bool
            }

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    # Prepare records for insertion
    records = []
    for goal in goals:
        records.append({
            'session_id': session_id,
            'member_id': goal['member_id'],
            'goal': goal['goal'],
            'is_vague': goal.get('is_vague', False),
            'is_completed': False
        })

    if records:
        supabase.table('goals').insert(records).execute()

    return True


def get_session_goals(session_id: int) -> List[dict]:
    """
    Get all goals for a session.

    Args:
        session_id: Session ID

    Returns:
        List of goals with member info
    """
    supabase = get_supabase()

    result = supabase.table('goals').select(
        '*, members(*)'
    ).eq('session_id', session_id).execute()

    return result.data


def update_goal_completion(goal_id: int, is_completed: bool) -> dict:
    """
    Update a goal's completion status.

    Args:
        goal_id: Goal ID
        is_completed: Completion status

    Returns:
        Updated goal record

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    result = supabase.table('goals').update({
        'is_completed': is_completed
    }).eq('id', goal_id).execute()

    return result.data[0] if result.data else None


def get_member_goals(member_id: int, limit: int = 10) -> List[dict]:
    """
    Get recent goals for a member.

    Args:
        member_id: Member ID
        limit: Number of recent goals to return

    Returns:
        List of goals
    """
    supabase = get_supabase()

    result = supabase.table('goals').select(
        '*, sessions(date, session_number)'
    ).eq('member_id', member_id).order('created_at', desc=True).limit(limit).execute()

    return result.data
