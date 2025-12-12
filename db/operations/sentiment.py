"""
Sentiment Operations

Operations for session_sentiment and session_sentiment_statements tables.
"""

from typing import List
from db.client import get_supabase


def save_sentiment(session_id: int, sentiment_data: dict) -> bool:
    """
    Save sentiment analysis for a session.

    Args:
        session_id: Session ID
        sentiment_data: Dict with structure:
            {
                'sentiment_score': int,
                'rationale': str,
                'dominant_emotion': str,
                'confidence_score': float,
                'representative_quotes': [
                    {
                        'member_id': int,
                        'emotions': List[str],
                        'exact_quotes': List[str],
                        'is_negative': bool
                    }
                ]
            }

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    # Insert session sentiment
    sentiment_result = supabase.table('session_sentiment').insert({
        'session_id': session_id,
        'sentiment_score': sentiment_data['sentiment_score'],
        'rationale': sentiment_data['rationale'],
        'dominant_emotion': sentiment_data['dominant_emotion'],
        'confidence_score': sentiment_data.get('confidence_score')
    }).execute()

    sentiment_id = sentiment_result.data[0]['id']

    # Insert sentiment statements
    statements = sentiment_data.get('representative_quotes', [])
    if statements:
        statement_records = []
        for statement in statements:
            statement_records.append({
                'session_sentiment_id': sentiment_id,
                'member_id': statement['member_id'],
                'emotions': statement.get('emotions', []),
                'exact_quotes': statement.get('exact_quotes', []),
                'is_negative': statement.get('is_negative', False)
            })

        if statement_records:
            supabase.table('session_sentiment_statements').insert(statement_records).execute()

    return True


def get_session_sentiment(session_id: int) -> dict:
    """
    Get sentiment analysis for a session with statements.

    Args:
        session_id: Session ID

    Returns:
        Sentiment data with statements
    """
    supabase = get_supabase()

    # Get sentiment
    sentiment_result = supabase.table('session_sentiment').select(
        '*'
    ).eq('session_id', session_id).execute()

    if not sentiment_result.data:
        return None

    sentiment = sentiment_result.data[0]

    # Get statements
    statements_result = supabase.table('session_sentiment_statements').select(
        '*, members(*)'
    ).eq('session_sentiment_id', sentiment['id']).execute()

    sentiment['statements'] = statements_result.data

    return sentiment


def get_group_sentiments(group_id: int, limit: int = 10) -> List[dict]:
    """
    Get recent sentiment analyses for a group.

    Args:
        group_id: Group ID
        limit: Number of recent sentiments to return

    Returns:
        List of sentiment analyses
    """
    supabase = get_supabase()

    # Get sessions for this group with sentiment
    result = supabase.table('sessions').select(
        'id, date, session_number, session_sentiment(*)'
    ).eq('group_id', group_id).order('date', desc=True).limit(limit).execute()

    return result.data
