"""
Challenges Operations

Operations for challenges and challenge_strategies tables.
"""

from typing import List
from db.client import get_supabase


def save_challenges(session_id: int, challenges: List[dict]) -> bool:
    """
    Save challenges and their strategies for a session.

    Args:
        session_id: Session ID
        challenges: List of challenge dicts with structure:
            {
                'member_id': int,
                'description': str,
                'category': str,
                'strategies': [
                    {
                        'suggested_by': int (member_id, optional),
                        'summary': str,
                        'tag': str
                    }
                ]
            }

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    for challenge in challenges:
        # Insert challenge
        challenge_result = supabase.table('challenges').insert({
            'session_id': session_id,
            'member_id': challenge['member_id'],
            'description': challenge['description'],
            'category': challenge.get('category')
        }).execute()

        challenge_id = challenge_result.data[0]['id']

        # Insert strategies for this challenge
        strategies = challenge.get('strategies', [])
        if strategies:
            strategy_records = []
            for strategy in strategies:
                strategy_records.append({
                    'challenge_id': challenge_id,
                    'suggested_by': strategy.get('suggested_by'),
                    'summary': strategy['summary'],
                    'tag': strategy.get('tag')
                })

            if strategy_records:
                supabase.table('challenge_strategies').insert(strategy_records).execute()

    return True


def get_session_challenges(session_id: int) -> List[dict]:
    """
    Get all challenges for a session with their strategies.

    Args:
        session_id: Session ID

    Returns:
        List of challenges with member info and strategies
    """
    supabase = get_supabase()

    # Get challenges
    challenges_result = supabase.table('challenges').select(
        '*, members(*)'
    ).eq('session_id', session_id).execute()

    challenges = challenges_result.data

    # Get strategies for each challenge
    for challenge in challenges:
        strategies_result = supabase.table('challenge_strategies').select(
            '*, suggested_by_member:members!challenge_strategies_suggested_by_fkey(*)'
        ).eq('challenge_id', challenge['id']).execute()

        challenge['strategies'] = strategies_result.data

    return challenges


def get_member_challenges(member_id: int, limit: int = 10) -> List[dict]:
    """
    Get recent challenges for a member.

    Args:
        member_id: Member ID
        limit: Number of recent challenges to return

    Returns:
        List of challenges with strategies
    """
    supabase = get_supabase()

    # Get challenges
    challenges_result = supabase.table('challenges').select(
        '*, sessions(date, session_number)'
    ).eq('member_id', member_id).order('created_at', desc=True).limit(limit).execute()

    challenges = challenges_result.data

    # Get strategies for each challenge
    for challenge in challenges:
        strategies_result = supabase.table('challenge_strategies').select(
            '*'
        ).eq('challenge_id', challenge['id']).execute()

        challenge['strategies'] = strategies_result.data

    return challenges
