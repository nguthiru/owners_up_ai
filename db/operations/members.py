"""
Member Operations

CRUD operations for members and group_members tables.
"""

from typing import List, Optional
from db.client import get_supabase
from db.models import Member, dict_to_member, GroupMember


def create_member(name: str, email: Optional[str] = None) -> Member:
    """
    Create a new member.

    Args:
        name: Member name
        email: Optional email address

    Returns:
        Created Member model

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    result = supabase.table('members').insert({
        'name': name,
        'email': email
    }).execute()

    return dict_to_member(result.data[0])


def get_member(member_id: int) -> Optional[Member]:
    """
    Get a member by ID.

    Args:
        member_id: Member ID

    Returns:
        Member model if found, None otherwise
    """
    supabase = get_supabase()

    result = supabase.table('members').select('*').eq('id', member_id).execute()

    return dict_to_member(result.data[0]) if result.data else None


def get_member_by_email(email: str) -> Optional[Member]:
    """
    Get a member by email.

    Args:
        email: Member email

    Returns:
        Member model if found, None otherwise
    """
    supabase = get_supabase()

    result = supabase.table('members').select('*').eq('email', email).execute()

    return dict_to_member(result.data[0]) if result.data else None


def list_members(active_only: bool = True) -> List[Member]:
    """
    List all members.

    Args:
        active_only: If True, only return active members

    Returns:
        List of Member models
    """
    supabase = get_supabase()

    query = supabase.table('members').select('*')

    if active_only:
        query = query.eq('is_active', True)

    result = query.order('name').execute()

    return [dict_to_member(row) for row in result.data]


def update_member(
    member_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None
) -> Member:
    """
    Update a member.

    Args:
        member_id: Member ID
        name: New name (optional)
        email: New email (optional)

    Returns:
        Updated Member model

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    update_data = {}
    if name is not None:
        update_data['name'] = name
    if email is not None:
        update_data['email'] = email

    result = supabase.table('members').update(update_data).eq('id', member_id).execute()

    return dict_to_member(result.data[0])


def assign_member_to_group(
    group_id: int,
    member_id: int,
    role: str = 'participant'
) -> dict:
    """
    Assign a member to a group.

    Args:
        group_id: Group ID
        member_id: Member ID
        role: Member role ('facilitator', 'participant', 'observer')

    Returns:
        Created GroupMember record as dict

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    result = supabase.table('group_members').insert({
        'group_id': group_id,
        'member_id': member_id,
        'role': role
    }).execute()

    return result.data[0]


def remove_member_from_group(group_id: int, member_id: int) -> bool:
    """
    Remove a member from a group by setting is_active to False.

    Args:
        group_id: Group ID
        member_id: Member ID

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    from datetime import datetime

    supabase.table('group_members').update({
        'is_active': False,
        'left_at': datetime.now().isoformat()
    }).eq('group_id', group_id).eq('member_id', member_id).execute()

    return True


def list_group_members(group_id: int, active_only: bool = True) -> List[dict]:
    """
    List all members in a group with their roles.

    Args:
        group_id: Group ID
        active_only: If True, only return active members

    Returns:
        List of dicts with member info and role
    """
    supabase = get_supabase()

    query = supabase.table('group_members').select(
        '*, members(*)'
    ).eq('group_id', group_id)

    if active_only:
        query = query.eq('is_active', True)

    result = query.order('members(name)').execute()

    return result.data


def list_member_groups(member_id: int, active_only: bool = True) -> List[dict]:
    """
    List all groups a member belongs to.

    Args:
        member_id: Member ID
        active_only: If True, only return active memberships

    Returns:
        List of dicts with group info and role
    """
    supabase = get_supabase()

    query = supabase.table('group_members').select(
        '*, groups(*)'
    ).eq('member_id', member_id)

    if active_only:
        query = query.eq('is_active', True)

    result = query.order('groups(name)').execute()

    return result.data


def update_member_role(group_id: int, member_id: int, role: str) -> dict:
    """
    Update a member's role in a group.

    Args:
        group_id: Group ID
        member_id: Member ID
        role: New role

    Returns:
        Updated GroupMember record as dict

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    result = supabase.table('group_members').update({
        'role': role
    }).eq('group_id', group_id).eq('member_id', member_id).execute()

    return result.data[0]
