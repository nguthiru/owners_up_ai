"""
OwnersUp Platform REST API

Complete REST API for the peer coaching platform with full CRUD serialize_date(operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
from typing import Optional
import os
from dotenv import load_dotenv

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
from db.operations import attendance as attendance_ops
from db.operations import goals as goals_ops
from db.operations import challenges as challenges_ops
from db.operations import stucks as stucks_ops
from db.operations import marketing as marketing_ops
from db.operations import sentiment as sentiment_ops

# Utils
from utils.name_matching import match_attendance_to_members
from utils.validators import validate_email, validate_slug, validate_transcript

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for Nextjs frontend

# Helper function to serialize dates
def serialize_date(date_value):
    """Convert date/datetime to ISO format string, or return as-is if already a serialize_date(string"""
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

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


# ============================================================================
# PROGRAMS ENDPOINTS
# ============================================================================

@app.route('/api/programs', methods=['GET'])
def list_programs():
    """List all programs"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        all_programs = programs.list_programs(active_only=active_only)

        return jsonify({
            "programs": [
                {
                                "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "description": p.description,
                    "is_active": p.is_active,
                    "created_at": serialize_date(p.created_at),
                    "updated_at": serialize_date(p.updated_at) if p.updated_at else None
                }
                for p in all_programs
            ]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/programs/<int:program_id>', methods=['GET'])
def get_program(program_id):
    """Get a single program by ID"""
    try:
        program = programs.get_program(program_id)
        if not program:
            return jsonify({"error": "Program not found"}), 404

        return jsonify({
                "id": program.id,
            "name": program.name,
            "slug": program.slug,
            "description": program.description,
            "is_active": program.is_active,
            "created_at": serialize_date(program.created_at),
            "updated_at": serialize_date(program.updated_at) if program.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/programs', methods=['POST'])
def create_program():
    """Create a new program"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        name = data.get('name')
        slug = data.get('slug')
        description = data.get('description')

        if not name:
            return jsonify({"error": "name is required"}), 400
        if not slug:
            return jsonify({"error": "slug is required"}), 400

        # Validate slug
        if not validate_slug(slug):
            return jsonify({"error": "Invalid slug format"}), 400

        program = programs.create_program(name, slug, description)

        return jsonify({
            "id": program.id,
            "name": program.name,
            "slug": program.slug,
            "description": program.description,
            "is_active": program.is_active,
            "created_at": serialize_date(program.created_at)
        }), 201
    except Exception as e:
        if "duplicate key" in str(e).lower():
            return jsonify({"error": "A program with this slug already exists"}), 409
        return jsonify({"error": str(e)}), 500


@app.route('/api/programs/<int:program_id>', methods=['PATCH'])
def update_program(program_id):
    """Update a program"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        program = programs.update_program(program_id, **data)
        if not program:
            return jsonify({"error": "Program not found"}), 404

        return jsonify({
                                        "id": program.id,
            "name": program.name,
            "slug": program.slug,
            "description": program.description,
            "is_active": program.is_active,
            "updated_at": program.updated_at.isoformat() if program.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/programs/<int:program_id>', methods=['DELETE'])
def delete_program(program_id):
    """Soft delete a program"""
    try:
        success = programs.delete_program(program_id)
        if not success:
            return jsonify({"error": "Program not found"}), 404

        return jsonify({"message": "Program deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# GROUPS ENDPOINTS
# ============================================================================

@app.route('/api/programs/<int:program_id>/groups', methods=['GET'])
def list_groups_by_program(program_id):
    """List all groups for a program"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        all_groups = groups.list_groups_by_program(program_id, active_only=active_only)

        return jsonify({
            "groups": [
                {
                    "id": g.id,
                    "program_id": g.program_id,
                    "name": g.name,
                    "cohort": g.cohort,
                    "start_date": serialize_date(g.start_date),
                    "end_date": serialize_date(g.end_date),
                    "is_active": g.is_active,
                    "created_at": serialize_date(g.created_at),
                    "updated_at": serialize_date(g.updated_at) if g.updated_at else None
                }
                for g in all_groups
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    """Get a single group by ID"""
    try:
        group = groups.get_group(group_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404

        return jsonify({
            "id": group.id,
            "program_id": group.program_id,
            "name": group.name,
            "cohort": group.cohort,
            "start_date": serialize_date(group.start_date),
            "end_date": serialize_date(group.end_date),
            "is_active": group.is_active,
            "created_at": serialize_date(group.created_at),
            "updated_at": serialize_date(group.updated_at) if group.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/groups', methods=['POST'])
def create_group():
    """Create a new group"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        program_id = data.get('program_id')
        name = data.get('name')
        cohort = data.get('cohort')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        if not program_id:
            return jsonify({"error": "program_id is required"}), 400
        if not name:
            return jsonify({"error": "name is required"}), 400

        # Parse dates
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        group = groups.create_group(program_id, name, cohort, start_date, end_date)

        return jsonify({
            "id": group.id,
                "program_id": group.program_id,
            "name": group.name,
            "cohort": group.cohort,
            "start_date": serialize_date(group.start_date),
            "end_date": serialize_date(group.end_date),
            "is_active": group.is_active,
            "created_at": serialize_date(group.created_at)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# MEMBERS ENDPOINTS
# ============================================================================

@app.route('/api/members', methods=['GET'])
def list_members():
    """List all members"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        all_members = members.list_members(active_only=active_only)

        return jsonify({
            "members": [
                {
                    "id": m.id,
                    "name": m.name,
                    "email": m.email,
                    "is_active": m.is_active,
                    "created_at": serialize_date(m.created_at),
                    "updated_at": serialize_date(m.updated_at) if m.updated_at else None
                }
                for m in all_members
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    """Get a single member by ID"""
    try:
        member = members.get_member(member_id)
        if not member:
            return jsonify({"error": "Member not found"}), 404

        return jsonify({
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "is_active": member.is_active,
            "created_at": serialize_date(member.created_at),
            "updated_at": serialize_date(member.updated_at) if member.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/members', methods=['POST'])
def create_member():
    """Create a new member"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        name = data.get('name')
        email = data.get('email')

        if not name:
            return jsonify({"error": "name is required"}), 400
        if not email:
            return jsonify({"error": "email is required"}), 400

        # Validate email
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        member = members.create_member(name, email)

        return jsonify({
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "is_active": member.is_active,
            "created_at": serialize_date(member.created_at)
        }), 201
    except Exception as e:
        if "duplicate key" in str(e).lower():
            return jsonify({"error": "A member with this email already exists"}), 409
        return jsonify({"error": str(e)}), 500


@app.route('/api/members/<int:member_id>/goals', methods=['GET'])
def get_member_goals(member_id):
    """Get goals for a specific member"""
    try:
        limit = request.args.get('limit', 50, type=int)
        member_goals = goals_ops.get_member_goals(member_id, limit)
        return jsonify({"goals": member_goals}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/members/<int:member_id>/challenges', methods=['GET'])
def get_member_challenges(member_id):
    """Get challenges for a specific member"""
    try:
        limit = request.args.get('limit', 50, type=int)
        member_challenges = challenges_ops.get_member_challenges(member_id, limit)
        return jsonify({"challenges": member_challenges}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/members/<int:member_id>/stucks', methods=['GET'])
def get_member_stucks(member_id):
    """Get stuck detections for a specific member"""
    try:
        limit = request.args.get('limit', 50, type=int)
        member_stucks = stucks_ops.get_member_stucks(member_id, limit)
        return jsonify({"stucks": member_stucks}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/members/<int:member_id>/marketing', methods=['GET'])
def get_member_marketing(member_id):
    """Get marketing activities for a specific member"""
    try:
        limit = request.args.get('limit', 50, type=int)
        member_marketing = marketing_ops.get_member_marketing(member_id, limit)
        return jsonify({"marketing": member_marketing}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/members/<int:member_id>/attendance', methods=['GET'])
def get_member_attendance(member_id):
    """Get attendance records for a specific member"""
    try:
        supabase = get_supabase()
        result = supabase.table('session_attendance').select(
            '*, sessions(id, date, session_number, groups(name))'
        ).eq('member_id', member_id).order('created_at', desc=True).execute()
        return jsonify({"attendance": result.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/members/<int:member_id>/groups', methods=['GET'])
def get_member_groups(member_id):
    """Get all groups a member belongs to"""
    try:
        member_groups = members.list_member_groups(member_id, active_only=True)
        return jsonify({"groups": member_groups}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/groups/<int:group_id>/members', methods=['GET'])
def list_group_members(group_id):
    """List all members in a group"""
    try:
        group_members_list = members.list_group_members(group_id)

        return jsonify({
            "members": [
                {
                    "group_member_id": gm['id'],
                    "group_id": gm['group_id'],
                    "member_id": gm['member_id'],
                    "role": gm['role'],
                    "joined_at": serialize_date(gm['joined_at']),
                    "member": {
                        "id": gm['members']['id'],
                        "name": gm['members']['name'],
                        "email": gm['members']['email']
                    }
                }
                for gm in group_members_list
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/group-members/<int:group_member_id>', methods=['DELETE'])
def remove_member_from_group(group_member_id):
    """Remove a member from a group by deactivating the group membership"""
    try:
        supabase = get_supabase()
        from datetime import datetime

        result = supabase.table('group_members').update({
            'is_active': False,
            'left_at': datetime.now().isoformat()
        }).eq('id', group_member_id).execute()

        if not result.data:
            return jsonify({"error": "Group membership not found"}), 404

        return jsonify({"message": "Member removed from group successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/groups/<int:group_id>/members', methods=['POST'])
def assign_member_to_group(group_id):
    """Assign a member to a group"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        member_id = data.get('member_id')
        role = data.get('role', 'participant')

        if not member_id:
            return jsonify({"error": "member_id is required"}), 400

        group_member = members.assign_member_to_group(group_id, member_id, role)

        return jsonify({
            "id": group_member['id'],
            "group_id": group_member['group_id'],
            "member_id": group_member['member_id'],
            "role": group_member['role'],
            "joined_at": serialize_date(group_member['joined_at'])
        }), 201
    except Exception as e:
        if "duplicate key" in str(e).lower():
            return jsonify({"error": "Member already assigned to this group"}), 409
        return jsonify({"error": str(e)}), 500


# ============================================================================
# SESSIONS ENDPOINTS
# ============================================================================

@app.route('/api/groups/<int:group_id>/sessions', methods=['GET'])
def list_sessions_by_group(group_id):
    """List all sessions for a group"""
    try:
        all_sessions = sessions.list_sessions_by_group(group_id)

        return jsonify({
            "sessions": [
                {
                    "id": s.id,
                    "group_id": s.group_id,
                    "session_number": s.session_number,
                    "session_date": serialize_date(s.date),
                    "notes": s.notes,
                    "transcript": s.transcript,
                    "created_at": serialize_date(s.created_at),
                    "updated_at": serialize_date(s.updated_at) if s.updated_at else None
                }
                for s in all_sessions
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get a single session by ID"""
    try:
        session = sessions.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        return jsonify({
            "id": session.id,
            "group_id": session.group_id,
            "session_number": session.session_number,
            "session_date": serialize_date(session.date),
            "notes": session.notes,
            "transcript": session.transcript,
            "created_at": serialize_date(session.created_at),
            "updated_at": serialize_date(session.updated_at) if session.updated_at else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new session"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        group_id = data.get('group_id')
        session_date_str = data.get('session_date')
        notes = data.get('notes')

        if not group_id:
            return jsonify({"error": "group_id is required"}), 400
        if not session_date_str:
            return jsonify({"error": "session_date is required"}), 400

        # Parse date
        session_date = datetime.fromisoformat(session_date_str) if session_date_str else None

        session = sessions.create_session(group_id, session_date, notes)

        return jsonify({
                    "id": session.id,
            "group_id": session.group_id,
            "session_number": session.session_number,
                    "session_date": serialize_date(session.date),
            "notes": session.notes,
            "created_at": serialize_date(session.created_at)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions/<int:session_id>/process-transcript', methods=['POST'])
def process_transcript(session_id):
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
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript is required"}), 400

        # Validate transcript
        is_valid, error = validate_transcript(transcript)
        if not is_valid:
            return jsonify({"error": error}), 400

        # Get session to verify it exists
        session = sessions.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

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
        return jsonify({
            "session_id": session_id,
            "extraction_results": {
                            "goals": goals_result.model_dump(mode='json'),
                "challenges": challenges_result.model_dump(mode='json'),
                "marketing_activities": marketing_result.model_dump(mode='json'),
                "stuck_detections": stucks_result.model_dump(mode='json'),
                "sentiment": sentiment_result.model_dump(mode='json'),
                "attendance": matched_attendance
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions/<int:session_id>/save-extractions', methods=['POST'])
def save_extractions(session_id):
    """
    Save AI extractions after frontend review/modification
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        extraction_results = data.get('extraction_results')

        if not extraction_results:
            return jsonify({"error": "extraction_results is required"}), 400

        # Get session to find group and members for name matching
        session = sessions.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

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
            return jsonify({"message": "Extractions saved successfully"}), 200
        else:
            return jsonify({"error": "Failed to save extractions"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# AI EXTRACTION ENDPOINTS (Original endpoints for standalone use)
# ============================================================================

@app.route('/api/extract/marketing-activities', methods=['POST'])
def extract_marketing_activities():
    """Extract marketing activities from transcript"""
    try:
        data = request.get_json()
        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript is required"}), 400

        result = get_marketing_activities(transcript)
        return jsonify(result.model_dump(mode='json')), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/extract/challenges', methods=['POST'])
def extract_challenges():
    """Extract challenges from transcript"""
    try:
        data = request.get_json()
        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript is required"}), 400

        result = get_challenges(transcript)
        return jsonify(result.model_dump(mode='json')), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/extract/goals', methods=['POST'])
def extract_goals():
    """Extract goals from transcript"""
    try:
        data = request.get_json()
        transcript = data.get('transcript')

        if not transcript:
            return jsonify({"error": "transcript is required"}), 400

        result = get_goals(transcript)
        return jsonify(result.model_dump(mode='json')), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/groups/<int:group_id>/analytics', methods=['GET'])
def get_group_analytics(group_id):
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
        total_sessions = supabase.table('sessions').select('id', count='exact').eq('group_id', group_id).execute()

        return jsonify({
            "group_id": group_id,
            "total_sessions": total_sessions.count or 0,
            "members": analytics_data
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 4000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
