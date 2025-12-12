/**
 * TypeScript types for OwnersUp Platform
 */

export interface Program {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface Group {
  id: number;
  program_id: number;
  name: string;
  cohort: string | null;
  start_date: string | null;
  end_date: string | null;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface Member {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface GroupMember {
  group_member_id: number;
  group_id: number;
  member_id: number;
  role: 'facilitator' | 'participant' | 'observer';
  joined_at: string | null;
  member: {
    id: number;
    name: string;
    email: string;
  };
}

export interface Session {
  id: number;
  group_id: number;
  session_number: number;
  session_date: string;
  notes: string | null;
  transcript: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface AttendanceRecord {
  extracted_name: string;
  status: 'present' | 'absent_without_updates' | 'travelling' | 'family_time' | 'work_business' | 'wellness';
  notes: string | null;
  matched_member_id: number | null;
  confidence_score: number;
  needs_manual_review: boolean;
}

export interface Goal {
  name: string;
  quantifiable_goal: string;
  is_vague: boolean;
}

export interface ChallengeStrategy {
  name: string | null;
  summary: string;
  tag: string;
}

export interface Challenge {
  challenge: string;
  category: string;
  strategies: ChallengeStrategy[];
}

export interface IndividualChallenges {
  name: string;
  challenges: Challenge[];
}

export interface MarketingOutcome {
  no_of_meetings: number;
  no_of_proposals: number;
  no_of_clients: number;
  notes: string;
}

export interface MarketingActivity {
  stage: string;
  activity: string;
  quanitity: number;
  outcome: MarketingOutcome;
  is_win: boolean;
  contract_type: string | null;
  revenue: number | null;
  client_involved: boolean;
}

export interface IndividualMarketingActivities {
  name: string | null;
  activities: MarketingActivity[];
}

export interface StuckDetection {
  name: string;
  classification: string;
  stuck_summary: string;
  exact_quotes: string[];
  potential_next_step: string;
}

export interface SessionSentiment {
  sentiment_score: number;
  rationale: string;
  dominant_emotion: string;
  representative_quotes: {
    name: string;
    emotion: string[];
    exact_quotes: string[];
    is_negative: boolean;
  }[];
  confidence_score: number;
}

export interface ExtractionResults {
  goals: { goals: Goal[] };
  challenges: { challenges: IndividualChallenges[] };
  marketing_activities: { activities: IndividualMarketingActivities[] };
  stuck_detections: { detections: StuckDetection[] };
  sentiment: SessionSentiment;
  attendance: AttendanceRecord[];
}

export interface ProcessTranscriptResponse {
  session_id: number;
  extraction_results: ExtractionResults;
}

// Form types
export interface CreateProgramInput {
  name: string;
  slug: string;
  description?: string;
}

export interface CreateGroupInput {
  program_id: number;
  name: string;
  cohort?: string;
  start_date?: string;
  end_date?: string;
}

export interface CreateMemberInput {
  name: string;
  email: string;
}

export interface CreateSessionInput {
  group_id: number;
  session_date: string;
  notes?: string;
}

export interface AssignMemberInput {
  member_id: number;
  role?: 'facilitator' | 'participant' | 'observer';
}
