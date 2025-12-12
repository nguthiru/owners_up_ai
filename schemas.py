"""
Pydantic Schemas for FastAPI

Request and response models for API validation and documentation.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# PROGRAM SCHEMAS
# ============================================================================

class ProgramBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProgramResponse(ProgramBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# GROUP SCHEMAS
# ============================================================================

class GroupBase(BaseModel):
    name: str
    cohort: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class GroupCreate(GroupBase):
    program_id: int


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    cohort: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class GroupResponse(GroupBase):
    id: int
    program_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# MEMBER SCHEMAS
# ============================================================================

class MemberBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None


class MemberCreate(MemberBase):
    email: EmailStr


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class MemberResponse(MemberBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# GROUP MEMBER SCHEMAS
# ============================================================================

class GroupMemberCreate(BaseModel):
    member_id: int
    role: str = "participant"


class GroupMemberResponse(BaseModel):
    group_member_id: int
    group_id: int
    member_id: int
    role: str
    joined_at: datetime
    member: MemberResponse

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SESSION SCHEMAS
# ============================================================================

class SessionBase(BaseModel):
    notes: Optional[str] = None


class SessionCreate(SessionBase):
    group_id: int
    session_date: datetime


class SessionUpdate(BaseModel):
    notes: Optional[str] = None
    transcript: Optional[str] = None


class SessionResponse(SessionBase):
    id: int
    group_id: int
    session_number: int
    session_date: datetime
    transcript: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# TRANSCRIPT PROCESSING SCHEMAS
# ============================================================================

class TranscriptProcessRequest(BaseModel):
    transcript: str


class TranscriptExtractionResults(BaseModel):
    goals: Dict[str, Any]
    challenges: Dict[str, Any]
    marketing_activities: Dict[str, Any]
    stuck_detections: Dict[str, Any]
    sentiment: Dict[str, Any]
    attendance: List[Dict[str, Any]]


class TranscriptProcessResponse(BaseModel):
    session_id: int
    extraction_results: TranscriptExtractionResults


class SaveExtractionsRequest(BaseModel):
    extraction_results: Dict[str, Any]


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class MemberStats(BaseModel):
    total_sessions: int
    attendance_rate: float
    total_goals: int
    completed_goals: int
    vague_goals: int
    challenges: int
    stuck_detections: int
    marketing_activities: int
    wins: int


class MemberAnalytics(BaseModel):
    member_id: int
    name: str
    email: Optional[str]
    role: str
    stats: MemberStats
    risk_level: str
    risk_score: int


class GroupAnalyticsResponse(BaseModel):
    group_id: int
    total_sessions: int
    members: List[MemberAnalytics]


# ============================================================================
# COMMON RESPONSE SCHEMAS
# ============================================================================

class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


# ============================================================================
# LIST RESPONSE SCHEMAS
# ============================================================================

class ProgramListResponse(BaseModel):
    programs: List[ProgramResponse]


class GroupListResponse(BaseModel):
    groups: List[GroupResponse]


class MemberListResponse(BaseModel):
    members: List[MemberResponse]


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]


class GroupMemberListResponse(BaseModel):
    members: List[GroupMemberResponse]
