"""
Marketing Activities Operations

Operations for marketing_activities and marketing_outcomes tables.
"""

from typing import List
from db.client import get_supabase


def save_marketing_activities(session_id: int, activities: List[dict]) -> bool:
    """
    Save marketing activities and outcomes for a session.

    Args:
        session_id: Session ID
        activities: List of marketing activity dicts with structure:
            {
                'member_id': int,
                'stage': str,
                'activity': str,
                'quantity': int,
                'is_win': bool,
                'contract_type': str (optional),
                'revenue': float (optional),
                'outcome': {
                    'no_of_meetings': int,
                    'no_of_proposals': int,
                    'no_of_clients': int,
                    'notes': str (optional)
                }
            }

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    for activity in activities:
        # Insert activity
        activity_result = supabase.table('marketing_activities').insert({
            'session_id': session_id,
            'member_id': activity['member_id'],
            'stage': activity['stage'],
            'activity': activity['activity'],
            'quantity': activity.get('quantity', 0),
            'is_win': activity.get('is_win', False),
            'contract_type': activity.get('contract_type'),
            'revenue': activity.get('revenue')
        }).execute()

        activity_id = activity_result.data[0]['id']

        # Insert outcome if provided
        outcome = activity.get('outcome')
        if outcome:
            supabase.table('marketing_outcomes').insert({
                'activity_id': activity_id,
                'no_of_meetings': outcome.get('no_of_meetings', 0),
                'no_of_proposals': outcome.get('no_of_proposals', 0),
                'no_of_clients': outcome.get('no_of_clients', 0),
                'notes': outcome.get('notes')
            }).execute()

    return True


def get_session_marketing(session_id: int) -> List[dict]:
    """
    Get all marketing activities for a session with outcomes.

    Args:
        session_id: Session ID

    Returns:
        List of marketing activities with member info and outcomes
    """
    supabase = get_supabase()

    # Get activities
    activities_result = supabase.table('marketing_activities').select(
        '*, members(*), marketing_outcomes(*)'
    ).eq('session_id', session_id).execute()

    return activities_result.data


def get_member_marketing(member_id: int, limit: int = 10) -> List[dict]:
    """
    Get recent marketing activities for a member.

    Args:
        member_id: Member ID
        limit: Number of recent activities to return

    Returns:
        List of marketing activities with outcomes
    """
    supabase = get_supabase()

    result = supabase.table('marketing_activities').select(
        '*, sessions(date, session_number), marketing_outcomes(*)'
    ).eq('member_id', member_id).order('created_at', desc=True).limit(limit).execute()

    return result.data
