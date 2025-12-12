"""
Attendance Operations

Operations for session_attendance table.
"""

from typing import List
from db.client import get_supabase


def save_attendance_records(session_id: int, attendance_records: List[dict]) -> bool:
    """
    Save attendance records for a session.

    Args:
        session_id: Session ID
        attendance_records: List of attendance dicts with structure:
            {
                'member_id': int,
                'status': str,
                'notes': str (optional)
            }

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    # Prepare records for upsert (insert or update if exists)
    records = []
    for record in attendance_records:
        records.append({
            'session_id': session_id,
            'member_id': record['member_id'],
            'status': record['status'],
            'notes': record.get('notes')
        })

    if records:
        # Use upsert to handle duplicates gracefully
        supabase.table('session_attendance').upsert(
            records,
            on_conflict='session_id,member_id'
        ).execute()

    return True


def get_session_attendance(session_id: int) -> List[dict]:
    """
    Get all attendance records for a session.

    Args:
        session_id: Session ID

    Returns:
        List of attendance records with member info
    """
    supabase = get_supabase()

    result = supabase.table('session_attendance').select(
        '*, members(*)'
    ).eq('session_id', session_id).execute()

    return result.data


def update_attendance_status(
    session_id: int,
    member_id: int,
    status: str,
    notes: str = None
) -> dict:
    """
    Update an attendance record.

    Args:
        session_id: Session ID
        member_id: Member ID
        status: New status
        notes: Optional notes

    Returns:
        Updated attendance record

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    update_data = {'status': status}
    if notes is not None:
        update_data['notes'] = notes

    result = supabase.table('session_attendance').update(update_data).eq(
        'session_id', session_id
    ).eq('member_id', member_id).execute()

    return result.data[0] if result.data else None
