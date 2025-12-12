"""
Database Models

Dataclass models representing database tables for type safety and convenience.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal


@dataclass
class Program:
    """Represents a program (e.g., CTOx, Founders Program)"""
    id: int
    name: str
    slug: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Group:
    """Represents a group within a program"""
    id: int
    program_id: int
    name: str
    cohort: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Member:
    """Represents a member/participant"""
    id: int
    name: str
    email: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool


@dataclass
class GroupMember:
    """Represents membership of a member in a group"""
    id: int
    group_id: int
    member_id: int
    role: str  # 'facilitator', 'participant', 'observer'
    joined_at: datetime
    left_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Session:
    """Represents a coaching session"""
    id: int
    group_id: int
    date: datetime
    session_number: int
    notes: Optional[str]
    transcript: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class SessionAttendance:
    """Represents attendance record for a session"""
    id: int
    session_id: int
    member_id: int
    status: str  # enum values from session_attendance_status
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class Goal:
    """Represents a member's goal from a session"""
    id: int
    member_id: int
    session_id: int
    goal: str
    is_vague: bool
    is_completed: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Challenge:
    """Represents a challenge discussed in a session"""
    id: int
    member_id: int
    session_id: int
    description: str
    category: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class ChallengeStrategy:
    """Represents a strategy suggested for a challenge"""
    id: int
    challenge_id: int
    suggested_by: Optional[int]
    summary: str
    tag: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class MemberStuck:
    """Represents a stuck detection for a member"""
    id: int
    member_id: int
    session_id: int
    classification: str
    stuck_summary: str
    exact_quotes: List[str]
    potential_next_step: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class MarketingActivity:
    """Represents a marketing activity from a session"""
    id: int
    member_id: int
    session_id: int
    stage: str  # enum: marketing_activity_stage
    activity: str  # enum: marketing_activity_type
    quantity: int
    is_win: bool
    contract_type: Optional[str]  # enum: marketing_activity_contract_type
    revenue: Optional[Decimal]
    created_at: datetime
    updated_at: datetime


@dataclass
class MarketingOutcome:
    """Represents outcomes of a marketing activity"""
    id: int
    activity_id: int
    no_of_meetings: int
    no_of_proposals: int
    no_of_clients: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class SessionSentiment:
    """Represents overall sentiment analysis of a session"""
    id: int
    session_id: int
    sentiment_score: int
    rationale: str
    dominant_emotion: str
    confidence_score: Optional[Decimal]
    created_at: datetime
    updated_at: datetime


@dataclass
class SessionSentimentStatement:
    """Represents individual sentiment statements from session participants"""
    id: int
    session_sentiment_id: int
    member_id: int
    emotions: List[str]
    exact_quotes: List[str]
    is_negative: bool
    created_at: datetime
    updated_at: datetime


# Helper functions for model conversion

def dict_to_program(data: dict) -> Program:
    """Convert database dict to Program model"""
    return Program(**data)


def dict_to_group(data: dict) -> Group:
    """Convert database dict to Group model"""
    return Group(**data)


def dict_to_member(data: dict) -> Member:
    """Convert database dict to Member model"""
    return Member(**data)


def dict_to_session(data: dict) -> Session:
    """Convert database dict to Session model"""
    return Session(**data)
