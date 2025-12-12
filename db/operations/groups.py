"""
Group Operations

CRUD operations for groups table.
"""

from typing import List, Optional
from datetime import date
from db.client import get_supabase
from db.models import Group, dict_to_group


def create_group(
    program_id: int,
    name: str,
    cohort: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Group:
    """
    Create a new group within a program.

    Args:
        program_id: Program ID
        name: Group name
        cohort: Optional cohort identifier
        start_date: Optional start date
        end_date: Optional end date

    Returns:
        Created Group model

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    data = {
        'program_id': program_id,
        'name': name,
        'cohort': cohort
    }

    if start_date:
        data['start_date'] = start_date.isoformat()
    if end_date:
        data['end_date'] = end_date.isoformat()

    result = supabase.table('groups').insert(data).execute()

    return dict_to_group(result.data[0])


def get_group(group_id: int) -> Optional[Group]:
    """
    Get a group by ID.

    Args:
        group_id: Group ID

    Returns:
        Group model if found, None otherwise
    """
    supabase = get_supabase()

    result = supabase.table('groups').select('*').eq('id', group_id).execute()

    return dict_to_group(result.data[0]) if result.data else None


def list_groups_by_program(program_id: int, active_only: bool = True) -> List[Group]:
    """
    List all groups in a program.

    Args:
        program_id: Program ID
        active_only: If True, only return active groups

    Returns:
        List of Group models
    """
    supabase = get_supabase()

    query = supabase.table('groups').select('*').eq('program_id', program_id)

    if active_only:
        query = query.eq('is_active', True)

    result = query.order('name').execute()

    return [dict_to_group(row) for row in result.data]


def list_all_groups(active_only: bool = True) -> List[Group]:
    """
    List all groups across all programs.

    Args:
        active_only: If True, only return active groups

    Returns:
        List of Group models
    """
    supabase = get_supabase()

    query = supabase.table('groups').select('*')

    if active_only:
        query = query.eq('is_active', True)

    result = query.order('name').execute()

    return [dict_to_group(row) for row in result.data]


def update_group(
    group_id: int,
    name: Optional[str] = None,
    cohort: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_active: Optional[bool] = None
) -> Group:
    """
    Update a group.

    Args:
        group_id: Group ID
        name: New name (optional)
        cohort: New cohort (optional)
        start_date: New start date (optional)
        end_date: New end date (optional)
        is_active: New active status (optional)

    Returns:
        Updated Group model

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    update_data = {}
    if name is not None:
        update_data['name'] = name
    if cohort is not None:
        update_data['cohort'] = cohort
    if start_date is not None:
        update_data['start_date'] = start_date.isoformat()
    if end_date is not None:
        update_data['end_date'] = end_date.isoformat()
    if is_active is not None:
        update_data['is_active'] = is_active

    result = supabase.table('groups').update(update_data).eq('id', group_id).execute()

    return dict_to_group(result.data[0])


def delete_group(group_id: int) -> bool:
    """
    Soft delete a group by setting is_active to False.

    Args:
        group_id: Group ID

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    supabase.table('groups').update({'is_active': False}).eq('id', group_id).execute()

    return True
