"""
Name Matching Utility

Fuzzy name matching using rapidfuzz to match AI-extracted names to database members.
"""

from rapidfuzz import fuzz, process
from typing import List, Tuple, Optional, Dict
from db.models import Member

# Import from config when available, default to 80
try:
    from config.constants import MATCH_THRESHOLD
except ImportError:
    MATCH_THRESHOLD = 80


def match_name_to_member(
    extracted_name: str,
    members: List[Member]
) -> Tuple[Optional[Member], int]:
    """
    Match an AI-extracted name to a member using fuzzy matching.

    Uses rapidfuzz's token_sort_ratio scorer which:
    - Handles different word orders ("John Smith" vs "Smith John")
    - Ignores case differences
    - Tolerates typos and missing/extra characters

    Args:
        extracted_name: Name extracted from transcript
        members: List of Member objects to match against

    Returns:
        Tuple of (matched_member, confidence_score) or (None, 0) if no match
        Confidence score is 0-100, where 100 is perfect match
    """
    if not extracted_name or not members:
        return None, 0

    # Create list of member names for matching
    member_names = [m.name for m in members]

    # Use rapidfuzz to find best match
    result = process.extractOne(
        extracted_name,
        member_names,
        scorer=fuzz.token_sort_ratio
    )

    if result and result[1] >= MATCH_THRESHOLD:
        matched_name, score, _ = result
        # Find the member object with this name
        matched_member = next(m for m in members if m.name == matched_name)
        return matched_member, int(score)

    # If no match meets threshold, return the best score anyway for info
    return None, int(result[1]) if result else 0


def match_attendance_to_members(
    attendance_data: dict,
    group_members: List[Member]
) -> List[Dict]:
    """
    Match all attendance records from AI extraction to group members.

    Args:
        attendance_data: Dict from AI extraction with structure:
            {
                'attendance': [
                    {
                        'name': str,
                        'status': str,
                        'notes': str (optional)
                    }
                ]
            }
        group_members: List of Member objects in the group

    Returns:
        List of matched attendance records with structure:
        {
            'extracted_name': str,
            'matched_member_id': int or None,
            'matched_member_name': str or None,
            'confidence': int (0-100),
            'status': str,
            'notes': str,
            'needs_manual_review': bool
        }
    """
    matched_attendance = []

    for record in attendance_data.get('attendance', []):
        extracted_name = record.get('name', '')
        status = record.get('status', 'present')
        notes = record.get('notes', '')

        # Try to match to a member
        matched_member, confidence = match_name_to_member(extracted_name, group_members)

        matched_attendance.append({
            'extracted_name': extracted_name,
            'matched_member_id': matched_member.id if matched_member else None,
            'matched_member_name': matched_member.name if matched_member else None,
            'matched_member_email': matched_member.email if matched_member else None,
            'confidence': confidence,
            'status': status,
            'notes': notes,
            'needs_manual_review': confidence < MATCH_THRESHOLD or matched_member is None
        })

    return matched_attendance


def match_goals_to_members(
    goals_data: dict,
    group_members: List[Member]
) -> List[Dict]:
    """
    Match goal records from AI extraction to group members.

    Args:
        goals_data: Dict from AI extraction with structure:
            {
                'goals': [
                    {
                        'name': str,
                        'quantifiable_goal': str,
                        'is_vague': bool
                    }
                ]
            }
        group_members: List of Member objects in the group

    Returns:
        List of matched goal records with structure:
        {
            'extracted_name': str,
            'matched_member_id': int or None,
            'matched_member_name': str or None,
            'confidence': int (0-100),
            'goal': str,
            'is_vague': bool,
            'needs_manual_review': bool
        }
    """
    matched_goals = []

    for goal in goals_data.get('goals', []):
        extracted_name = goal.get('name', '')
        goal_text = goal.get('quantifiable_goal', '')
        is_vague = goal.get('is_vague', False)

        # Try to match to a member
        matched_member, confidence = match_name_to_member(extracted_name, group_members)

        matched_goals.append({
            'extracted_name': extracted_name,
            'matched_member_id': matched_member.id if matched_member else None,
            'matched_member_name': matched_member.name if matched_member else None,
            'confidence': confidence,
            'goal': goal_text,
            'is_vague': is_vague,
            'needs_manual_review': confidence < MATCH_THRESHOLD or matched_member is None or not goal_text
        })

    return matched_goals


def batch_match_names_to_members(
    extracted_names: List[str],
    group_members: List[Member]
) -> Dict[str, Tuple[Optional[Member], int]]:
    """
    Match multiple extracted names to members in one call.

    Args:
        extracted_names: List of names extracted from transcript
        group_members: List of Member objects to match against

    Returns:
        Dict mapping extracted_name -> (matched_member, confidence_score)
    """
    matches = {}

    for name in extracted_names:
        matched_member, confidence = match_name_to_member(name, group_members)
        matches[name] = (matched_member, confidence)

    return matches


def get_match_suggestions(
    extracted_name: str,
    members: List[Member],
    top_n: int = 3
) -> List[Tuple[Member, int]]:
    """
    Get top N member suggestions for a name that didn't match.

    Useful for manual review UI where user can select from suggestions.

    Args:
        extracted_name: Name extracted from transcript
        members: List of Member objects
        top_n: Number of suggestions to return

    Returns:
        List of (Member, confidence_score) tuples, ordered by score desc
    """
    if not extracted_name or not members:
        return []

    member_names = [m.name for m in members]

    # Get top N matches
    results = process.extract(
        extracted_name,
        member_names,
        scorer=fuzz.token_sort_ratio,
        limit=top_n
    )

    suggestions = []
    for matched_name, score, _ in results:
        member = next(m for m in members if m.name == matched_name)
        suggestions.append((member, int(score)))

    return suggestions
