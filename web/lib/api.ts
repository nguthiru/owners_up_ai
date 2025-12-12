/**
 * API Client for OwnersUp Platform
 * Handles all HTTP requests to the Flask backend
 */

import type {
  Program,
  Group,
  Member,
  GroupMember,
  Session,
  ProcessTranscriptResponse,
  ExtractionResults,
  CreateProgramInput,
  CreateGroupInput,
  CreateMemberInput,
  CreateSessionInput,
  AssignMemberInput,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new APIError(response.status, error.error || `HTTP ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown'}`);
  }
}

// ============================================================================
// PROGRAMS API
// ============================================================================

export const programsAPI = {
  list: async (activeOnly = true): Promise<{ programs: Program[] }> => {
    return fetchAPI(`/api/programs?active_only=${activeOnly}`);
  },

  get: async (id: number): Promise<Program> => {
    return fetchAPI(`/api/programs/${id}`);
  },

  create: async (data: CreateProgramInput): Promise<Program> => {
    return fetchAPI(`/api/programs`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (id: number, data: Partial<CreateProgramInput>): Promise<Program> => {
    return fetchAPI(`/api/programs/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  delete: async (id: number): Promise<{ message: string }> => {
    return fetchAPI(`/api/programs/${id}`, {
      method: 'DELETE',
    });
  },
};

// ============================================================================
// GROUPS API
// ============================================================================

export const groupsAPI = {
  listByProgram: async (programId: number, activeOnly = true): Promise<{ groups: Group[] }> => {
    return fetchAPI(`/api/programs/${programId}/groups?active_only=${activeOnly}`);
  },

  get: async (id: number): Promise<Group> => {
    return fetchAPI(`/api/groups/${id}`);
  },

  create: async (data: CreateGroupInput): Promise<Group> => {
    return fetchAPI(`/api/groups`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: async (id: number, data: Partial<CreateGroupInput>): Promise<Group> => {
    return fetchAPI(`/api/groups/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  getAnalytics: async (groupId: number): Promise<any> => {
    return fetchAPI(`/api/groups/${groupId}/analytics`);
  },
};

// ============================================================================
// MEMBERS API
// ============================================================================

export const membersAPI = {
  list: async (activeOnly = true): Promise<{ members: Member[] }> => {
    return fetchAPI(`/api/members?active_only=${activeOnly}`);
  },

  get: async (id: number): Promise<Member> => {
    return fetchAPI(`/api/members/${id}`);
  },

  create: async (data: CreateMemberInput): Promise<Member> => {
    return fetchAPI(`/api/members`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  listGroupMembers: async (groupId: number): Promise<{ members: GroupMember[] }> => {
    return fetchAPI(`/api/groups/${groupId}/members`);
  },

  assignToGroup: async (groupId: number, data: AssignMemberInput): Promise<GroupMember> => {
    return fetchAPI(`/api/groups/${groupId}/members`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getGoals: async (memberId: number, limit = 50): Promise<{ goals: any[] }> => {
    return fetchAPI(`/api/members/${memberId}/goals?limit=${limit}`);
  },

  getChallenges: async (memberId: number, limit = 50): Promise<{ challenges: any[] }> => {
    return fetchAPI(`/api/members/${memberId}/challenges?limit=${limit}`);
  },

  getStucks: async (memberId: number, limit = 50): Promise<{ stucks: any[] }> => {
    return fetchAPI(`/api/members/${memberId}/stucks?limit=${limit}`);
  },

  getMarketing: async (memberId: number, limit = 50): Promise<{ marketing: any[] }> => {
    return fetchAPI(`/api/members/${memberId}/marketing?limit=${limit}`);
  },

  getAttendance: async (memberId: number): Promise<{ attendance: any[] }> => {
    return fetchAPI(`/api/members/${memberId}/attendance`);
  },

  getGroups: async (memberId: number): Promise<{ groups: any[] }> => {
    return fetchAPI(`/api/members/${memberId}/groups`);
  },
};

// ============================================================================
// SESSIONS API
// ============================================================================

export const sessionsAPI = {
  listByGroup: async (groupId: number): Promise<{ sessions: Session[] }> => {
    return fetchAPI(`/api/groups/${groupId}/sessions`);
  },

  get: async (id: number): Promise<Session> => {
    return fetchAPI(`/api/sessions/${id}`);
  },

  create: async (data: CreateSessionInput): Promise<Session> => {
    return fetchAPI(`/api/sessions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  processTranscript: async (sessionId: number, transcript: string): Promise<ProcessTranscriptResponse> => {
    return fetchAPI(`/api/sessions/${sessionId}/process-transcript`, {
      method: 'POST',
      body: JSON.stringify({ transcript }),
    });
  },

  saveExtractions: async (sessionId: number, extractionResults: ExtractionResults): Promise<{ message: string }> => {
    return fetchAPI(`/api/sessions/${sessionId}/save-extractions`, {
      method: 'POST',
      body: JSON.stringify({ extraction_results: extractionResults }),
    });
  },
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthAPI = {
  check: async (): Promise<{ status: string; timestamp: string }> => {
    return fetchAPI(`/health`);
  },
};

export { APIError };
