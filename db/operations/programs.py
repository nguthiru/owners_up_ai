"""
Program Operations

CRUD operations for programs table.
"""

from typing import List, Optional
from db.client import get_supabase
from db.models import Program, dict_to_program


def create_program(name: str, slug: str, description: Optional[str] = None) -> Program:
    """
    Create a new program.

    Args:
        name: Program name
        slug: URL-friendly slug
        description: Optional program description

    Returns:
        Created Program model

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    result = supabase.table('programs').insert({
        'name': name,
        'slug': slug,
        'description': description
    }).execute()

    return dict_to_program(result.data[0])


def get_program(program_id: int) -> Optional[Program]:
    """
    Get a program by ID.

    Args:
        program_id: Program ID

    Returns:
        Program model if found, None otherwise
    """
    supabase = get_supabase()

    result = supabase.table('programs').select('*').eq('id', program_id).execute()

    return dict_to_program(result.data[0]) if result.data else None


def get_program_by_slug(slug: str) -> Optional[Program]:
    """
    Get a program by slug.

    Args:
        slug: Program slug

    Returns:
        Program model if found, None otherwise
    """
    supabase = get_supabase()

    result = supabase.table('programs').select('*').eq('slug', slug).execute()

    return dict_to_program(result.data[0]) if result.data else None


def list_programs(active_only: bool = True) -> List[Program]:
    """
    List all programs.

    Args:
        active_only: If True, only return active programs

    Returns:
        List of Program models
    """
    supabase = get_supabase()

    query = supabase.table('programs').select('*')

    if active_only:
        query = query.eq('is_active', True)

    result = query.order('name').execute()

    return [dict_to_program(row) for row in result.data]


def update_program(
    program_id: int,
    name: Optional[str] = None,
    slug: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Program:
    """
    Update a program.

    Args:
        program_id: Program ID
        name: New name (optional)
        slug: New slug (optional)
        description: New description (optional)
        is_active: New active status (optional)

    Returns:
        Updated Program model

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    update_data = {}
    if name is not None:
        update_data['name'] = name
    if slug is not None:
        update_data['slug'] = slug
    if description is not None:
        update_data['description'] = description
    if is_active is not None:
        update_data['is_active'] = is_active

    result = supabase.table('programs').update(update_data).eq('id', program_id).execute()

    return dict_to_program(result.data[0])


def delete_program(program_id: int) -> bool:
    """
    Soft delete a program by setting is_active to False.

    Args:
        program_id: Program ID

    Returns:
        True if successful

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase()

    supabase.table('programs').update({'is_active': False}).eq('id', program_id).execute()

    return True
