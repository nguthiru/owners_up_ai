-- ====================================================================================
-- PEER COACHING PLATFORM - INITIAL SCHEMA MIGRATION
-- ====================================================================================
-- This migration creates the complete database schema for the peer coaching platform
-- Including: programs, groups, members, sessions, and all AI extraction tables
-- ====================================================================================

-- ====================================================================================
-- 1. CREATE ENUMS
-- ====================================================================================

CREATE TYPE group_member_role AS ENUM (
    'facilitator',
    'participant',
    'observer'
);

CREATE TYPE session_attendance_status AS ENUM (
    'present',
    'absent_without_updates',
    'travelling',
    'family_time',
    'work_business',
    'wellness'
);

CREATE TYPE marketing_activity_stage AS ENUM (
    'none_mentioned',
    'meetings',
    'proposals',
    'closed'
);

CREATE TYPE marketing_activity_type AS ENUM (
    'none_mentioned',
    'network_activation',
    'linkedin',
    'cold_outreach'
);

CREATE TYPE marketing_activity_contract_type AS ENUM (
    'one_time',
    'monthly',
    'hybrid'
);

-- ====================================================================================
-- 2. CREATE TABLES
-- ====================================================================================

-- Programs Table
CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    slug VARCHAR UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Groups Table
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    program_id INTEGER NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    cohort VARCHAR,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Members Table
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Group Members (Junction Table)
CREATE TABLE group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    role group_member_role DEFAULT 'participant',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(group_id, member_id)
);

-- Sessions Table
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    date TIMESTAMPTZ NOT NULL,
    session_number INTEGER,
    notes TEXT,
    transcript TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session Attendance Table
CREATE TABLE session_attendance (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    status session_attendance_status NOT NULL,
    notes VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, member_id)
);

-- Goals Table
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    goal VARCHAR NOT NULL,
    is_vague BOOLEAN DEFAULT false,
    is_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Challenges Table
CREATE TABLE challenges (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    description VARCHAR NOT NULL,
    category VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Challenge Strategies Table
CREATE TABLE challenge_strategies (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    suggested_by INTEGER REFERENCES members(id) ON DELETE SET NULL,
    summary VARCHAR NOT NULL,
    tag VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Member Stucks Table
CREATE TABLE member_stucks (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    classification VARCHAR NOT NULL,
    stuck_summary VARCHAR NOT NULL,
    exact_quotes TEXT[],
    potential_next_step VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Marketing Activities Table
CREATE TABLE marketing_activities (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    stage marketing_activity_stage NOT NULL,
    activity marketing_activity_type NOT NULL,
    quantity INTEGER DEFAULT 0,
    is_win BOOLEAN DEFAULT false,
    contract_type marketing_activity_contract_type,
    revenue DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Marketing Outcomes Table
CREATE TABLE marketing_outcomes (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER UNIQUE NOT NULL REFERENCES marketing_activities(id) ON DELETE CASCADE,
    no_of_meetings INTEGER DEFAULT 0,
    no_of_proposals INTEGER DEFAULT 0,
    no_of_clients INTEGER DEFAULT 0,
    notes VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session Sentiment Table
CREATE TABLE session_sentiment (
    id SERIAL PRIMARY KEY,
    session_id INTEGER UNIQUE NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    sentiment_score INTEGER NOT NULL,
    rationale VARCHAR NOT NULL,
    dominant_emotion VARCHAR NOT NULL,
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session Sentiment Statements Table
CREATE TABLE session_sentiment_statements (
    id SERIAL PRIMARY KEY,
    session_sentiment_id INTEGER NOT NULL REFERENCES session_sentiment(id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    emotions VARCHAR[],
    exact_quotes TEXT[],
    is_negative BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ====================================================================================
-- 3. CREATE INDEXES FOR PERFORMANCE
-- ====================================================================================

-- Programs indexes
CREATE INDEX idx_programs_slug ON programs(slug);
CREATE INDEX idx_programs_is_active ON programs(is_active);

-- Groups indexes
CREATE INDEX idx_groups_program_id ON groups(program_id);
CREATE INDEX idx_groups_is_active ON groups(is_active);

-- Members indexes
CREATE INDEX idx_members_email ON members(email);

-- Group Members indexes
CREATE INDEX idx_group_members_group_id ON group_members(group_id);
CREATE INDEX idx_group_members_member_id ON group_members(member_id);
CREATE INDEX idx_group_members_is_active ON group_members(is_active);

-- Sessions indexes
CREATE INDEX idx_sessions_group_id ON sessions(group_id);
CREATE INDEX idx_sessions_date ON sessions(date);
CREATE INDEX idx_sessions_group_date ON sessions(group_id, date);

-- Session Attendance indexes
CREATE INDEX idx_session_attendance_session_id ON session_attendance(session_id);
CREATE INDEX idx_session_attendance_member_id ON session_attendance(member_id);

-- Goals indexes
CREATE INDEX idx_goals_session_id ON goals(session_id);
CREATE INDEX idx_goals_member_id ON goals(member_id);
CREATE INDEX idx_goals_is_completed ON goals(is_completed);

-- Challenges indexes
CREATE INDEX idx_challenges_session_id ON challenges(session_id);
CREATE INDEX idx_challenges_member_id ON challenges(member_id);
CREATE INDEX idx_challenges_category ON challenges(category);

-- Challenge Strategies indexes
CREATE INDEX idx_challenge_strategies_challenge_id ON challenge_strategies(challenge_id);
CREATE INDEX idx_challenge_strategies_suggested_by ON challenge_strategies(suggested_by);

-- Member Stucks indexes
CREATE INDEX idx_member_stucks_session_id ON member_stucks(session_id);
CREATE INDEX idx_member_stucks_member_id ON member_stucks(member_id);

-- Marketing Activities indexes
CREATE INDEX idx_marketing_activities_session_id ON marketing_activities(session_id);
CREATE INDEX idx_marketing_activities_member_id ON marketing_activities(member_id);
CREATE INDEX idx_marketing_activities_is_win ON marketing_activities(is_win);

-- Marketing Outcomes indexes
CREATE INDEX idx_marketing_outcomes_activity_id ON marketing_outcomes(activity_id);

-- Session Sentiment indexes
CREATE INDEX idx_session_sentiment_session_id ON session_sentiment(session_id);

-- Session Sentiment Statements indexes
CREATE INDEX idx_sentiment_statements_sentiment_id ON session_sentiment_statements(session_sentiment_id);
CREATE INDEX idx_sentiment_statements_member_id ON session_sentiment_statements(member_id);

-- ====================================================================================
-- 4. CREATE TRIGGERS FOR AUTOMATIC UPDATED_AT
-- ====================================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_programs_updated_at
    BEFORE UPDATE ON programs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_groups_updated_at
    BEFORE UPDATE ON groups
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_members_updated_at
    BEFORE UPDATE ON members
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_group_members_updated_at
    BEFORE UPDATE ON group_members
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_session_attendance_updated_at
    BEFORE UPDATE ON session_attendance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goals_updated_at
    BEFORE UPDATE ON goals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_challenges_updated_at
    BEFORE UPDATE ON challenges
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_challenge_strategies_updated_at
    BEFORE UPDATE ON challenge_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_member_stucks_updated_at
    BEFORE UPDATE ON member_stucks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_marketing_activities_updated_at
    BEFORE UPDATE ON marketing_activities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_marketing_outcomes_updated_at
    BEFORE UPDATE ON marketing_outcomes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_session_sentiment_updated_at
    BEFORE UPDATE ON session_sentiment
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_session_sentiment_statements_updated_at
    BEFORE UPDATE ON session_sentiment_statements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ====================================================================================
-- 5. CREATE AUTO-INCREMENT SESSION NUMBER FUNCTION
-- ====================================================================================

-- Function to auto-increment session_number per group
CREATE OR REPLACE FUNCTION set_session_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.session_number IS NULL THEN
        SELECT COALESCE(MAX(session_number), 0) + 1
        INTO NEW.session_number
        FROM sessions
        WHERE group_id = NEW.group_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically set session_number
CREATE TRIGGER auto_session_number
    BEFORE INSERT ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION set_session_number();

-- ====================================================================================
-- END OF MIGRATION
-- ====================================================================================

-- Verification query (optional - run separately to verify)
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
