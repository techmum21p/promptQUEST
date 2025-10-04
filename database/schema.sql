-- PostgreSQL Database Schema for Prompt Training App
-- This script creates the database structure for user management and progress tracking

-- Create database (run this separately as superuser if needed)
-- CREATE DATABASE prompt_training_db;

-- Connect to the database
-- \c prompt_training_db;

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for user authentication and profile information
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ldap_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_address VARCHAR(255) UNIQUE NOT NULL,
    user_group VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- User progress tracking table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ldap_id VARCHAR(50) NOT NULL, -- Denormalized for easier queries
    attempt_number INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scenario_id VARCHAR(10) NOT NULL,
    user_prompt TEXT,
    total_score INTEGER NOT NULL DEFAULT 0,
    clarity_score INTEGER NOT NULL DEFAULT 0,
    specificity_score INTEGER NOT NULL DEFAULT 0,
    structure_score INTEGER NOT NULL DEFAULT 0,
    task_alignment_score INTEGER NOT NULL DEFAULT 0,
    skill_level VARCHAR(20) NOT NULL DEFAULT 'beginner',
    feedback TEXT,
    strengths TEXT[], -- Array of strength strings
    improvements TEXT[], -- Array of improvement strings
    session_id VARCHAR(100), -- Optional session tracking
    
    -- Data integrity constraints
    CONSTRAINT valid_scores CHECK (
        total_score >= 0 AND total_score <= 100 AND
        clarity_score >= 0 AND clarity_score <= 25 AND
        specificity_score >= 0 AND specificity_score <= 25 AND
        structure_score >= 0 AND structure_score <= 25 AND
        task_alignment_score >= 0 AND task_alignment_score <= 25 AND
        total_score = clarity_score + specificity_score + structure_score + task_alignment_score
    ),
    CONSTRAINT valid_skill_level CHECK (skill_level IN ('beginner', 'intermediate', 'advanced')),
    CONSTRAINT valid_scenario_id CHECK (scenario_id ~ '^[abi]\d+$')
);

-- User badges table for awarded achievements
CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_name VARCHAR(100) NOT NULL,
    awarded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scenario_id VARCHAR(10), -- Optional: scenario where badge was earned
    
    CONSTRAINT unique_user_badge UNIQUE(user_id, badge_name)
);

-- Leaderboard view for easy access to ranking data
CREATE MATERIALIZED VIEW leaderboard AS
SELECT 
    u.ldap_id,
    u.username,
    u.user_group,
    COUNT(up.id) as total_attempts,
    CASE 
        WHEN COUNT(up.id) = 0 THEN 0
        ELSE ROUND(AVG(up.total_score)::NUMERIC, 2)
    END as avg_score,
    MAX(up.skill_level) as current_skill_level,
    COUNT(ub.id) as total_badges,
    MAX(up.timestamp) as last_activity,
    ARRAY_AGG(DISTINCT ub.badge_name ORDER BY ub.badge_name) FILTER (WHERE ub.badge_name IS NOT NULL) as badges
FROM users u
LEFT JOIN user_progress up ON u.id = up.user_id
LEFT JOIN user_badges ub ON u.id = ub.user_id AND ub.badge_name IS NOT NULL
WHERE u.is_active = TRUE
GROUP BY u.id, u.ldap_id, u.username, u.user_group
ORDER BY avg_score DESC, total_attempts DESC;

-- Indexes for performance optimization
CREATE INDEX idx_users_ldap_id ON users(ldap_id);
CREATE INDEX idx_users_email ON users(email_address);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_group ON users(user_group);

CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_user_progress_ldap_id ON user_progress(ldap_id);
CREATE INDEX idx_user_progress_timestamp ON user_progress(timestamp);
CREATE INDEX idx_user_progress_scenario ON user_progress(scenario_id);
CREATE INDEX idx_user_progress_score ON user_progress(total_score);
CREATE INDEX idx_user_progress_skill_level ON user_progress(skill_level);
CREATE INDEX idx_user_progress_session ON user_progress(session_id);

CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX idx_user_badges_name ON user_badges(badge_name);

-- Trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to refresh leaderboard materialized view
CREATE OR REPLACE FUNCTION refresh_leaderboard()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW leaderboard;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_leaderboard_on_progress_change
    AFTER INSERT OR UPDATE OR DELETE ON user_progress
    FOR EACH ROW EXECUTE FUNCTION refresh_leaderboard();

CREATE TRIGGER update_leaderboard_on_badge_change
    AFTER INSERT OR UPDATE OR DELETE ON user_badges
    FOR EACH ROW EXECUTE FUNCTION refresh_leaderboard();

CREATE TRIGGER update_leaderboard_on_user_change
    AFTER UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION refresh_leaderboard();

-- Function to update user stats after new progress entry
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS TRIGGER AS $$
DECLARE
    user_avg_score NUMERIC;
    user_skill_level VARCHAR(20);
BEGIN
    -- Calculate average score and determine skill level
    SELECT 
        CASE WHEN COUNT(*) = 0 THEN 0 ELSE ROUND(AVG(total_score)::NUMERIC, 2) END,
        CASE 
            WHEN COUNT(*) < 3 THEN 'beginner'
            WHEN COUNT(*) >= 5 AND AVG(total_score) >= 85 THEN 'advanced'
            WHEN COUNT(*) >= 3 AND AVG(total_score) >= 70 THEN 'intermediate'
            ELSE 'beginner'
        END
    INTO user_avg_score, user_skill_level
    FROM user_progress 
    WHERE user_id = NEW.user_id AND ldap_id = NEW.ldap_id;
    
    -- Update the current progress entry with computed skill level
    UPDATE user_progress 
    SET skill_level = user_skill_level
    WHERE id = NEW.id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_stats_on_progress
    AFTER INSERT ON user_progress
    FOR EACH ROW EXECUTE FUNCTION update_user_stats();

-- Views for common queries

-- User summary view
CREATE VIEW user_summary AS
SELECT 
    u.id,
    u.ldap_id,
    u.username,
    u.user_group,
    u.email_address,
    u.created_at,
    u.last_login,
    COUNT(up.id) as total_attempts,
    CASE 
        WHEN COUNT(up.id) = 0 THEN 0
        ELSE ROUND(AVG(up.total_score)::NUMERIC, 2)
    END as avg_score,
    MAX(up.skill_level) as current_skill_level,
    COUNT(ub.id) as total_badges,
    MAX(up.timestamp) as last_activity
FROM users u
LEFT JOIN user_progress up ON u.id = up.user_id
LEFT JOIN user_badges ub ON u.id = ub.user_id
WHERE u.is_active = TRUE
GROUP BY u.id, u.ldap_id, u.username, u.user_group, u.email_address, u.created_at, u.last_login;

-- Scenario performance view
CREATE VIEW scenario_performance AS
SELECT 
    scenario_id,
    COUNT(*) as total_attempts,
    ROUND(AVG(total_score)::NUMERIC, 2) as avg_score,
    MIN(total_score) as min_score,
    MAX(total_score) as max_score,
    ROUND(STDDEV(total_score)::NUMERIC, 2) as score_stddev,
    COUNT(DISTINCT user_id) as unique_users,
    ROUND(AVG(clarity_score)::NUMERIC, 2) as avg_clarity,
    ROUND(AVG(specificity_score)::NUMERIC, 2) as avg_specificity,
    ROUND(AVG(structure_score)::NUMERIC, 2) as avg_structure,
    ROUND(AVG(task_alignment_score)::NUMERIC, 2) as avg_task_alignment
FROM user_progress
GROUP BY scenario_id
ORDER BY avg_score DESC;

-- Initial refresh of materialized view
REFRESH MATERIALIZED VIEW leaderboard;

-- Sample INSERT statements for testing (commented out)
/*
INSERT INTO users (ldap_id, username, password_hash, email_address, user_group) 
VALUES 
    ('user001', 'testuser', '$2b$12$example_hash', 'test@company.com', 'engineering'),
    ('admin001', 'admin', '$2b$12$admin_hash', 'admin@company.com', 'admin');
*/
