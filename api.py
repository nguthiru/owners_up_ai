"""
OwnersUp Platform REST API

Complete REST API for the peer coaching platform with full CRUD operations
Converted from Flask to FastAPI
"""

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv

# Pydantic schemas
from schemas import (
    ProgramCreate, ProgramUpdate, ProgramResponse, ProgramListResponse,
    GroupCreate, GroupResponse, GroupListResponse,
    MemberCreate, MemberResponse, MemberListResponse,
    GroupMemberCreate, GroupMemberListResponse,
    SessionCreate, SessionResponse, SessionListResponse,
    TranscriptProcessRequest, TranscriptProcessResponse, SaveExtractionsRequest,
    MessageResponse, HealthResponse, GroupAnalyticsResponse
)

# AI extraction functions
from ai.functions import (
    get_marketing_activities,
    get_challenges,
    get_attendance,
    get_goals,
    get_stuck_detections,
    get_call_sentiment
)

# Database operations
from db.client import get_supabase
from db.operations import programs, groups, members, sessions
from db.operations import goals as goals_ops
from db.operations import challenges as challenges_ops
from db.operations import stucks as stucks_ops
from db.operations import marketing as marketing_ops

# Utils
from utils.name_matching import match_attendance_to_members
from utils.validators import validate_email, validate_slug, validate_transcript

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="OwnersUp Platform API",
    description="REST API for the peer coaching platform",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function to serialize dates
def serialize_date(date_value):
    """Convert date/datetime to ISO format string, or return as-is if already a string"""
    if date_value is None:
        return None
    if isinstance(date_value, str):
        return date_value
    if hasattr(date_value, 'isoformat'):
        return date_value.isoformat()
    return str(date_value)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get('/health', response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}


# ============================================================================
# PROGRAMS ENDPOINTS
# ============================================================================

@app.get('/api/programs', response_model=ProgramListResponse, tags=["Programs"])
async def list_programs(active_only: bool = Query(True, description="Filter by active status")):
    """List all programs"""
    try:
        all_programs = programs.list_programs(active_only=active_only)

        return {
            "programs": [
                {
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "description": p.description,
                    "is_active": p.is_active,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at
                }
                for p in all_programs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/programs/{program_id}', response_model=ProgramResponse, tags=["Programs"])
async def get_program(program_id: int):
    """Get a single program by ID"""
    try:
        program = programs.get_program(program_id)
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")

        return {
            "id": program.id,
            "name": program.name,
            "slug": program.slug,
            "description": program.description,
            "is_active": program.is_active,
            "created_at": program.created_at,
            "updated_at": program.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/programs', response_model=ProgramResponse, status_code=status.HTTP_201_CREATED, tags=["Programs"])
async def create_program(program: ProgramCreate):
    """Create a new program"""
    try:
        # Validate slug
        if not validate_slug(program.slug):
            raise HTTPException(status_code=400, detail="Invalid slug format")

        new_program = programs.create_program(program.name, program.slug, program.description)

        return {
            "id": new_program.id,
            "name": new_program.name,
            "slug": new_program.slug,
            "description": new_program.description,
            "is_active": new_program.is_active,
            "created_at": new_program.created_at,
            "updated_at": new_program.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=409, detail="A program with this slug already exists")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch('/api/programs/{program_id}', response_model=ProgramResponse, tags=["Programs"])
async def update_program(program_id: int, program_update: ProgramUpdate):
    """Update a program"""
    try:
        updated_program = programs.update_program(program_id, **program_update.model_dump(exclude_unset=True))
        if not updated_program:
            raise HTTPException(status_code=404, detail="Program not found")

        return {
            "id": updated_program.id,
            "name": updated_program.name,
            "slug": updated_program.slug,
            "description": updated_program.description,
            "is_active": updated_program.is_active,
            "created_at": updated_program.created_at,
            "updated_at": updated_program.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/api/programs/{program_id}', response_model=MessageResponse, tags=["Programs"])
async def delete_program(program_id: int):
    """Soft delete a program"""
    try:
        success = programs.delete_program(program_id)
        if not success:
            raise HTTPException(status_code=404, detail="Program not found")

        return {"message": "Program deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GROUPS ENDPOINTS
# ============================================================================

@app.get('/api/programs/{program_id}/groups', response_model=GroupListResponse, tags=["Groups"])
async def list_groups_by_program(program_id: int, active_only: bool = Query(True)):
    """List all groups for a program"""
    try:
        all_groups = groups.list_groups_by_program(program_id, active_only=active_only)

        return {
            "groups": [
                {
                    "id": g.id,
                    "program_id": g.program_id,
                    "name": g.name,
                    "cohort": g.cohort,
                    "start_date": g.start_date,
                    "end_date": g.end_date,
                    "is_active": g.is_active,
                    "created_at": g.created_at,
                    "updated_at": g.updated_at
                }
                for g in all_groups
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/groups/{group_id}', response_model=GroupResponse, tags=["Groups"])
async def get_group(group_id: int):
    """Get a single group by ID"""
    try:
        group = groups.get_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        return {
            "id": group.id,
            "program_id": group.program_id,
            "name": group.name,
            "cohort": group.cohort,
            "start_date": group.start_date,
            "end_date": group.end_date,
            "is_active": group.is_active,
            "created_at": group.created_at,
            "updated_at": group.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/groups', response_model=GroupResponse, status_code=status.HTTP_201_CREATED, tags=["Groups"])
async def create_group(group: GroupCreate):
    """Create a new group"""
    try:
        new_group = groups.create_group(
            group.program_id,
            group.name,
            group.cohort,
            group.start_date,
            group.end_date
        )

        return {
            "id": new_group.id,
            "program_id": new_group.program_id,
            "name": new_group.name,
            "cohort": new_group.cohort,
            "start_date": new_group.start_date,
            "end_date": new_group.end_date,
            "is_active": new_group.is_active,
            "created_at": new_group.created_at,
            "updated_at": new_group.updated_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MEMBERS ENDPOINTS
# ============================================================================

@app.get('/api/members', response_model=MemberListResponse, tags=["Members"])
async def list_members(active_only: bool = Query(True)):
    """List all members"""
    try:
        all_members = members.list_members(active_only=active_only)

        return {
            "members": [
                {
                    "id": m.id,
                    "name": m.name,
                    "email": m.email,
                    "is_active": m.is_active,
                    "created_at": m.created_at,
                    "updated_at": m.updated_at
                }
                for m in all_members
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/members/{member_id}', response_model=MemberResponse, tags=["Members"])
async def get_member(member_id: int):
    """Get a single member by ID"""
    try:
        member = members.get_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        return {
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "is_active": member.is_active,
            "created_at": member.created_at,
            "updated_at": member.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/members', response_model=MemberResponse, status_code=status.HTTP_201_CREATED, tags=["Members"])
async def create_member(member: MemberCreate):
    """Create a new member"""
    try:
        # Validate email
        if not validate_email(member.email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        new_member = members.create_member(member.name, member.email)

        return {
            "id": new_member.id,
            "name": new_member.name,
            "email": new_member.email,
            "is_active": new_member.is_active,
            "created_at": new_member.created_at,
            "updated_at": new_member.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=409, detail="A member with this email already exists")
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/members/{member_id}/goals', tags=["Members"])
async def get_member_goals(member_id: int, limit: int = Query(50, ge=1, le=500)):
    """Get goals for a specific member"""
    try:
        member_goals = goals_ops.get_member_goals(member_id, limit)
        return {"goals": member_goals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/members/{member_id}/challenges', tags=["Members"])
async def get_member_challenges(member_id: int, limit: int = Query(50, ge=1, le=500)):
    """Get challenges for a specific member"""
    try:
        member_challenges = challenges_ops.get_member_challenges(member_id, limit)
        return {"challenges": member_challenges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/members/{member_id}/stucks', tags=["Members"])
async def get_member_stucks(member_id: int, limit: int = Query(50, ge=1, le=500)):
    """Get stuck detections for a specific member"""
    try:
        member_stucks = stucks_ops.get_member_stucks(member_id, limit)
        return {"stucks": member_stucks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/members/{member_id}/marketing', tags=["Members"])
async def get_member_marketing(member_id: int, limit: int = Query(50, ge=1, le=500)):
    """Get marketing activities for a specific member"""
    try:
        member_marketing = marketing_ops.get_member_marketing(member_id, limit)
        return {"marketing": member_marketing}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/members/{member_id}/attendance', tags=["Members"])
async def get_member_attendance(member_id: int):
    """Get attendance records for a specific member"""
    try:
        supabase = get_supabase()
        result = supabase.table('session_attendance').select(
            '*, sessions(id, date, session_number, groups(name))'
        ).eq('member_id', member_id).order('created_at', desc=True).execute()
        return {"attendance": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/members/{member_id}/groups', tags=["Members"])
async def get_member_groups(member_id: int):
    """Get all groups a member belongs to"""
    try:
        member_groups = members.list_member_groups(member_id, active_only=True)
        return {"groups": member_groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/groups/{group_id}/members', response_model=GroupMemberListResponse, tags=["Groups", "Members"])
async def list_group_members(group_id: int):
    """List all members in a group"""
    try:
        group_members_list = members.list_group_members(group_id)

        return {
            "members": [
                {
                    "group_member_id": gm['id'],
                    "group_id": gm['group_id'],
                    "member_id": gm['member_id'],
                    "role": gm['role'],
                    "joined_at": gm['joined_at'],
                    "member": {
                        "id": gm['members']['id'],
                        "name": gm['members']['name'],
                        "email": gm['members']['email'],
                        "is_active": gm['members'].get('is_active', True),
                        "created_at": gm['members'].get('created_at'),
                        "updated_at": gm['members'].get('updated_at')
                    }
                }
                for gm in group_members_list
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/api/group-members/{group_member_id}', response_model=MessageResponse, tags=["Members"])
async def remove_member_from_group(group_member_id: int):
    """Remove a member from a group by deactivating the group membership"""
    try:
        supabase = get_supabase()

        result = supabase.table('group_members').update({
            'is_active': False,
            'left_at': datetime.now().isoformat()
        }).eq('id', group_member_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Group membership not found")

        return {"message": "Member removed from group successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/groups/{group_id}/members', status_code=status.HTTP_201_CREATED, tags=["Groups", "Members"])
async def assign_member_to_group(group_id: int, group_member: GroupMemberCreate):
    """Assign a member to a group"""
    try:
        new_group_member = members.assign_member_to_group(
            group_id,
            group_member.member_id,
            group_member.role
        )

        return {
            "id": new_group_member['id'],
            "group_id": new_group_member['group_id'],
            "member_id": new_group_member['member_id'],
            "role": new_group_member['role'],
            "joined_at": serialize_date(new_group_member['joined_at'])
        }
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=409, detail="Member already assigned to this group")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SESSIONS ENDPOINTS
# ============================================================================

@app.get('/api/groups/{group_id}/sessions', response_model=SessionListResponse, tags=["Sessions"])
async def list_sessions_by_group(group_id: int):
    """List all sessions for a group"""
    try:
        all_sessions = sessions.list_sessions_by_group(group_id)

        return {
            "sessions": [
                {
                    "id": s.id,
                    "group_id": s.group_id,
                    "session_number": s.session_number,
                    "session_date": s.date,
                    "notes": s.notes,
                    "transcript": s.transcript,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at
                }
                for s in all_sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/sessions/{session_id}', response_model=SessionResponse, tags=["Sessions"])
async def get_session(session_id: int):
    """Get a single session by ID"""
    try:
        session = sessions.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "id": session.id,
            "group_id": session.group_id,
            "session_number": session.session_number,
            "session_date": session.date,
            "notes": session.notes,
            "transcript": session.transcript,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/sessions', response_model=SessionResponse, status_code=status.HTTP_201_CREATED, tags=["Sessions"])
async def create_session(session: SessionCreate):
    """Create a new session"""
    try:
        new_session = sessions.create_session(
            session.group_id,
            session.session_date,
            session.notes
        )

        return {
            "id": new_session.id,
            "group_id": new_session.group_id,
            "session_number": new_session.session_number,
            "session_date": new_session.date,
            "notes": new_session.notes,
            "transcript": new_session.transcript,
            "created_at": new_session.created_at,
            "updated_at": new_session.updated_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/sessions/{session_id}/process-transcript', response_model=TranscriptProcessResponse, tags=["Sessions", "AI"])
async def process_transcript(session_id: int, request: TranscriptProcessRequest):
    """
    Process transcript with AI extraction and save all results

    This endpoint:
    1. Receives transcript text
    2. Runs all AI extractions in parallel
    3. Matches names to members
    4. Returns results for frontend review
    5. Saves to database after frontend confirmation
    """
    try:
        transcript = request.transcript

        # Validate transcript
        is_valid, error = validate_transcript(transcript)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)

        # Get session to verify it exists
        session = sessions.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get group members for name matching
        group_members_data = members.list_group_members(session.group_id)
        member_names = ", ".join([gm['members']['name'] for gm in group_members_data])

        # Convert group members to Member objects for name matching
        from db.models import Member
        member_objects = [
            Member(
                id=gm['members']['id'],
                name=gm['members']['name'],
                email=gm['members']['email'],
                created_at=gm['members'].get('created_at'),
                updated_at=gm['members'].get('updated_at'),
                is_active=gm['members'].get('is_active', True)
            )
            for gm in group_members_data
        ]

        # Run AI extractions
        goals_result = get_goals(transcript)
        challenges_result = get_challenges(transcript)
        marketing_result = get_marketing_activities(transcript)
        stucks_result = get_stuck_detections(transcript)
        sentiment_result = get_call_sentiment(transcript)
        attendance_result = get_attendance(member_names, transcript)

        # Match attendance names to members
        matched_attendance = match_attendance_to_members(
            attendance_result.model_dump(),
            member_objects
        )

        # Update session with transcript
        sessions.update_session(session_id, transcript=transcript)

        # Return results for frontend review
        return {
            "session_id": session_id,
            "extraction_results": {
                "goals": goals_result.model_dump(mode='json'),
                "challenges": challenges_result.model_dump(mode='json'),
                "marketing_activities": marketing_result.model_dump(mode='json'),
                "stuck_detections": stucks_result.model_dump(mode='json'),
                "sentiment": sentiment_result.model_dump(mode='json'),
                "attendance": matched_attendance
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/sessions/{session_id}/save-extractions', response_model=MessageResponse, tags=["Sessions", "AI"])
async def save_extractions(session_id: int, request: SaveExtractionsRequest):
    """
    Save AI extractions after frontend review/modification
    """
    try:
        extraction_results = request.extraction_results

        # Get session to find group and members for name matching
        session = sessions.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get group members to build name -> ID mapping
        group_members_data = members.list_group_members(session.group_id)
        name_to_id = {}
        for gm in group_members_data:
            name_to_id[gm['members']['name']] = gm['members']['id']

        # Extract individual components
        attendance_raw = extraction_results.get('attendance', [])
        goals_raw = extraction_results.get('goals', {}).get('goals', [])
        challenges_raw = extraction_results.get('challenges', {}).get('challenges', [])
        marketing_raw = extraction_results.get('marketing_activities', {}).get('activities', [])
        stucks_raw = extraction_results.get('stuck_detections', {}).get('detections', [])
        sentiment_raw = extraction_results.get('sentiment', {})

        # Helper function to normalize enum values
        def normalize_enum_value(value):
            """Convert AI enum values to database format (lowercase with underscores)"""
            if not value:
                return 'none_mentioned'
            # Convert to lowercase and replace spaces with underscores
            return value.lower().replace(' ', '_').replace('/', '_')

        # Transform attendance records (frontend format -> DB format)
        attendance = []
        for record in attendance_raw:
            if record.get('matched_member_id'):
                attendance.append({
                    'member_id': record['matched_member_id'],
                    'status': normalize_enum_value(record.get('status', 'present')),
                    'notes': record.get('notes')
                })

        # Transform goals (with name -> ID mapping)
        goals = []
        for goal in goals_raw:
            member_name = goal.get('name')
            if member_name and member_name in name_to_id:
                goals.append({
                    'member_id': name_to_id[member_name],
                    'goal': goal.get('quantifiable_goal', ''),
                    'is_vague': goal.get('is_vague', False)
                })

        # Transform challenges (flatten nested structure with name -> ID mapping)
        challenges = []
        for individual in challenges_raw:
            member_name = individual.get('name')
            if member_name and member_name in name_to_id:
                member_id = name_to_id[member_name]
                for challenge in individual.get('challenges', []):
                    # Transform strategies to use member_id for suggested_by
                    strategies = []
                    for strategy in challenge.get('strategies', []):
                        strategy_copy = dict(strategy)
                        suggested_by_name = strategy.get('name')
                        if suggested_by_name and suggested_by_name in name_to_id:
                            strategy_copy['suggested_by'] = name_to_id[suggested_by_name]
                        else:
                            strategy_copy['suggested_by'] = None
                        # Remove 'name' field as DB expects 'suggested_by'
                        strategy_copy.pop('name', None)
                        strategies.append(strategy_copy)

                    challenges.append({
                        'member_id': member_id,
                        'description': challenge.get('challenge', ''),
                        'category': challenge.get('category', ''),
                        'strategies': strategies
                    })

        # Transform marketing activities (flatten nested structure with name -> ID mapping)
        marketing_activities = []
        for individual in marketing_raw:
            member_name = individual.get('name')
            if member_name and member_name in name_to_id:
                member_id = name_to_id[member_name]
                for activity in individual.get('activities', []):
                    marketing_activities.append({
                        'member_id': member_id,
                        'stage': normalize_enum_value(activity.get('stage', '')),
                        'activity': normalize_enum_value(activity.get('activity', '')),
                        'quantity': activity.get('quanitity', 0),
                        'outcome': activity.get('outcome', {}),
                        'is_win': activity.get('is_win', False),
                        'contract_type': normalize_enum_value(activity.get('contract_type')) if activity.get('contract_type') else None,
                        'revenue': activity.get('revenue')
                    })

        # Transform stucks (with name -> ID mapping)
        stucks = []
        for stuck in stucks_raw:
            member_name = stuck.get('name')
            if member_name and member_name in name_to_id:
                stucks.append({
                    'member_id': name_to_id[member_name],
                    'classification': stuck.get('classification', ''),
                    'stuck_summary': stuck.get('stuck_summary', ''),
                    'exact_quotes': stuck.get('exact_quotes', []),
                    'potential_next_step': stuck.get('potential_next_step', '')
                })

        # Transform sentiment (with name -> ID mapping for quotes)
        sentiment = {}
        if sentiment_raw:
            representative_quotes = []
            for quote in sentiment_raw.get('representative_quotes', []):
                member_name = quote.get('name')
                if member_name and member_name in name_to_id:
                    representative_quotes.append({
                        'member_id': name_to_id[member_name],
                        'emotions': quote.get('emotion', []),
                        'exact_quotes': quote.get('exact_quotes', []),
                        'is_negative': quote.get('is_negative', False)
                    })

            sentiment = {
                'sentiment_score': sentiment_raw.get('sentiment_score', 3),
                'rationale': sentiment_raw.get('rationale', ''),
                'dominant_emotion': sentiment_raw.get('dominant_emotion', ''),
                'confidence_score': sentiment_raw.get('confidence_score', 0.5),
                'representative_quotes': representative_quotes
            }

        # Save all extractions atomically
        success = sessions.save_session_extractions(
            session_id,
            attendance,
            goals,
            challenges,
            marketing_activities,
            stucks,
            sentiment
        )

        if success:
            return {"message": "Extractions saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save extractions")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI EXTRACTION ENDPOINTS (Original endpoints for standalone use)
# ============================================================================

@app.post('/api/extract/marketing-activities', tags=["AI", "Extraction"])
async def extract_marketing_activities(request: TranscriptProcessRequest):
    """Extract marketing activities from transcript"""
    try:
        result = get_marketing_activities(request.transcript)
        return result.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/extract/challenges', tags=["AI", "Extraction"])
async def extract_challenges(request: TranscriptProcessRequest):
    """Extract challenges from transcript"""
    try:
        result = get_challenges(request.transcript)
        return result.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/extract/goals', tags=["AI", "Extraction"])
async def extract_goals(request: TranscriptProcessRequest):
    """Extract goals from transcript"""
    try:
        result = get_goals(request.transcript)
        return result.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get('/api/groups/{group_id}/analytics', response_model=GroupAnalyticsResponse, tags=["Analytics"])
async def get_group_analytics(group_id: int):
    """Get comprehensive analytics for a group including risk ratings"""
    try:
        supabase = get_supabase()

        # Get group members
        group_members = members.list_group_members(group_id, active_only=True)

        analytics_data = []

        for gm in group_members:
            member_data = gm['members']
            member_id = member_data['id']

            # Get member analytics
            member_goals = goals_ops.get_member_goals(member_id, limit=100)
            member_challenges = challenges_ops.get_member_challenges(member_id, limit=100)
            member_stucks = stucks_ops.get_member_stucks(member_id, limit=100)
            member_marketing = marketing_ops.get_member_marketing(member_id, limit=100)

            # Get attendance for this group only
            attendance_result = supabase.table('session_attendance').select(
                '*, sessions!inner(group_id)'
            ).eq('member_id', member_id).eq('sessions.group_id', group_id).execute()

            attendance_records = attendance_result.data
            total_sessions = len(attendance_records)
            present_count = len([a for a in attendance_records if a['status'] == 'present'])
            attendance_rate = (present_count / total_sessions * 100) if total_sessions > 0 else 0

            # Calculate goal completion
            total_goals = len(member_goals)
            completed_goals = len([g for g in member_goals if g.get('is_completed')])
            vague_goals = len([g for g in member_goals if g.get('is_vague')])

            # Calculate risk level
            risk_level = "on_track"  # default
            risk_score = 0

            # High risk factors
            absent_count = len([a for a in attendance_records if a['status'] != 'present'])
            if absent_count >= 2:
                risk_score += 3

            # Check recent activity (last 2 weeks)
            from datetime import datetime, timedelta, timezone
            two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)

            recent_goals = [g for g in member_goals
                          if g.get('created_at') and datetime.fromisoformat(g['created_at'].replace('Z', '+00:00')) > two_weeks_ago]
            if len(recent_goals) == 0 and total_sessions > 0:
                risk_score += 2

            # Stuck detections
            if len(member_stucks) >= 2:
                risk_score += 2

            # Medium risk factors
            if absent_count == 1:
                risk_score += 1

            # Check for wins (crushing it)
            has_wins = any(m.get('is_win') for m in member_marketing)
            has_revenue = any(m.get('revenue') for m in member_marketing if m.get('revenue') and float(m['revenue']) > 0)

            if has_wins or has_revenue:
                risk_level = "crushing_it"
            elif risk_score >= 4:
                risk_level = "high_risk"
            elif risk_score >= 2:
                risk_level = "medium_risk"

            analytics_data.append({
                "member_id": member_id,
                "name": member_data['name'],
                "email": member_data['email'],
                "role": gm['role'],
                "stats": {
                    "total_sessions": total_sessions,
                    "attendance_rate": round(attendance_rate, 1),
                    "total_goals": total_goals,
                    "completed_goals": completed_goals,
                    "vague_goals": vague_goals,
                    "challenges": len(member_challenges),
                    "stuck_detections": len(member_stucks),
                    "marketing_activities": len(member_marketing),
                    "wins": len([m for m in member_marketing if m.get('is_win')]),
                },
                "risk_level": risk_level,
                "risk_score": risk_score
            })

        # Calculate group-level stats
        total_sessions_result = supabase.table('sessions').select('id', count='exact').eq('group_id', group_id).execute()

        return {
            "group_id": group_id,
            "total_sessions": total_sessions_result.count or 0,
            "members": analytics_data
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 4000))
    uvicorn.run("api:app", host='0.0.0.0', port=port, reload=True)
