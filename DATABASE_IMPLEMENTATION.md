# PostgreSQL Database Implementation for Prompt Training App

This document outlines the PostgreSQL database implementation for the Prompt Training App, designed to replace the JSON/CSV storage system with a robust, scalable database solution.

## Overview

The database implementation provides:
- **User authentication and management** with LDAP integration
- **Progress tracking and analytics** with detailed scoring breakdowns
- **Badge and achievement system** with automated awarding
- **Leaderboard and ranking system** with materialized views
- **Batch processing** for efficient data handling
- **Session management** with automatic flushing

## Database Schema

### Core Tables

#### 1. Users Table (`users`)
```sql
- id (UUID, Primary Key)
- ldap_id (VARCHAR, Unique) - LDAP identifier
- username (VARCHAR, Unique) - Display name
- password_hash (VARCHAR) - Hashed password
- email_address (VARCHAR, Unique) - Email address
- user_group (VARCHAR) - Organizational group/department
- created_at (TIMESTAMP) - Account creation time
- updated_at (TIMESTAMP) - Last update time
- isn_login (TIMESTAMP) - Last login time
- is_active (BOOLEAN) - Account status
```

#### 2. User Progress Table (`user_progress`)
```sql
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key) - References users.id
- ldap_id (VARCHAR) - Denormalized for query performance
- attempt_number (INTEGER) - Sequential attempt number
- timestamp (TIMESTAMP) - When attempt was made
- scenario_id (VARCHAR) - Scenario identifier (e.g., 'b1', 'i2')
- user_prompt (TEXT) - User's prompt text
- total_score (INTEGER) - Overall score (0-100)
- clarity_score (INTEGER) - Clarity score (0-25)
- specificity_score (INTEGER) - Specificity score (0-25)
- structure_score (INTEGER) - Structure score (0-25)
- task_alignment_score (INTEGER) - Task alignment score (0-25)
- skill_level (VARCHAR) - Current skill level
- feedback (TEXT) - Evaluation feedback
- strengths (TEXT[]) - Array of strengths
- improvements (TEXT[]) - Array of improvements
- session_id (VARCHAR) - Session identifier
```

#### 3. User Badges Table (`user_badges`)
```sql
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key) - References users.id
- badge_name (VARCHAR) - Name of the badge
- awarded_at (TIMESTAMP) - When badge was awarded
- scenario_id (VARCHAR) - Scenario where badge was earned
- UNIQUE(user_id, badge_name) - Prevent duplicate badges
```

### Views and Materialized Views

#### Leaderboard Materialized View (`leaderboard`)
Pre-computed rankings with:
- User statistics (attempts, average score, badges)
- Automatic refresh on progress updates
- Grouped sorting capabilities

#### Scenario Performance View (`scenario_performance`)
Analytics view showing:
- Performance metrics per scenario
- Average scores and distributions
- Difficulty analysis

## Architecture Highlights

### 1. Efficient Design Patterns

**Denormalization**: `ldap_id` is stored in both `users` and `user_progress` tables for faster queries without joins.

**Materialized Views**: Leaderboard is pre-computed for performance rather than calculated on-demand.

**Indexing Strategy**: Comprehensive indexes on frequently queried columns:
- User lookups (ldap_id, email, username)
- Progress queries (timestamp, scenario_id, score)
- Session tracking (session_id)

### 2. Data Integrity

**Constraints**: 
- Score validation (0-100 total, 0-25 per component)
- Valid skill levels ('beginner', 'intermediate', 'advanced')
- Scenario ID format validation

**Triggers**:
- Automatic skill level updates based on performance
- Materialized view refresh on data changes
- Timestamp management

### 3. Scalability Features

**Connection Pooling**: Async connection management with configurable pool sizes.

**Batch Operations**: Efficient bulk inserts for session data.

**Session-based Processing**: Temporary storage with automatic flushing.

## Implementation Files

### Database Core
- `database/schema.sql` - Complete database schema
- `database/config.py` - Connection configuration and management
- `database/service.py` - Service layer with CRUD operations

### Application Integration
- `prompt_training_app_db.py` - Main application with PostgreSQL
- `batch_manager.py` - Session and batch processing
- `database/setup.py` - Setup and migration utilities

### Configuration
- `env-example-db.env` - Environment variables template
- `requirements-db.txt` - Database dependencies

### Testing
- `test_database_integration.py` - Comprehensive test suite

## Key Features Implemented

### 1. User Management
```python
# User registration
user = await user_service.create_user(UserData(...))

# Authentication
authenticated_user = await tracker.authenticate_user("ldap_id", "password")

# User lookup by various fields
user_by_ldap = await user_service.get_user_by_ldap_id("user001")
user_by_email = await user_service.get_user_by_email("user@company.com")
```

### 2. Progress Tracking
```python
# Record attempt
await tracker.record_attempt(ldap_id, scenario_id, score, evaluation, prompt)

# Get user statistics
stats = await tracker.get_user_stats(ldap_id)
# Returns: total_attempts, avg_score, skill_level, badges, etc.

# Progress summary with leaderboard data
summary = await progress_service.get_user_progress_summary(ldap_id)
```

### 3. Batch Processing
```python
# Automatic batch processing every 5 attempts
progress_data = ProgressData(...)
await batch_manager.add_progress_entry(user_ldap_id, progress_data)

# Manual flushing
await batch_manager.manual_flush_session(user_ldap_id)

# Session management
session_id = await batch_manager.start_session(user_ldap_id)
await batch_manager.end_session(user_ldap_id)
```

### 4. Badge System
```python
# Award badge
badge = await badge_service.award_badge(user_id, "Perfect Score", scenario_id)

# Automated badge checking
new_badges = await badge_service.check_and_award_badges(ldap_id, progress_data)

# Badge types implemented:
# - Perfect Score (100 points)
# - Consistent Performer (avg > 80, attempts >= 3)
# - Dedicated Learner (attempts >= 10)
# - Advanced Master (advanced scenarios, avg > 85)
```

### 5. Leaderboard System
```python
# Get top performers
leaderboard = await tracker.get_leaderboard(top_n=10)

# Group-based leaderboards
engineering_leaders = await tracker.get_leaderboard(group="engineering")

# Leaderboard includes:
# - Username, LDAP ID, group
# - Total attempts, average score
# - Current skill level, badge count
# - Last activity timestamp
```

## Performance Optimizations

### 1. Batch Processing Strategy
- **Session-based buffering**: Store attempts in memory
- **Automatic flushing**: Every 5 attempts or session end
- **Efficient bulk inserts**: Single transaction for multiple entries

### 2. Database Optimizations
- **Indexes**: Optimized for common query patterns
- **Materialized views**: Pre-computed leaderboard
- **Connection pooling**: Reuse database connections
- **Async operations**: Non-blocking database calls

### 3. Memory Management
- **Periodic cleanup**: Remove expired sessions
- **Configurable thresholds**: Adjustable flush frequencies
- **Memory monitoring**: Track session usage

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements-db.txt
```

### 2. Configure Environment
```bash
cp env-example-db.env .env
# Edit .env with your PostgreSQL credentials
```

### 3. Setup Database
```bash
# Create database and tables
python database/setup.py --action setup

# Verify setup
python database/setup.py --action verify
```

### 4. Test Integration
```bash
# Quick test
python test_database_integration.py quick

# Comprehensive test
python test_database_integration.py
```

## Migration from Original System

### Data Export Strategy
The original JSON/CSV data can be migrated using:

1. **CSV Import**: Update existing CSV exports to include LDAP IDs
2. **User Creation**: Create user accounts for existing users
3. **Progress Migration**: Import historical progress data
4. **Badge Migration**: Award legacy badges based on performance

### Compatibility Features
- **Dual operation**: Can run alongside original system during transition
- **Data export**: Compatible export formats for migration tools
- **Configuration**: Same scenarios and evaluation logic

## Monitoring and Maintenance

### Database Health Monitoring
```python
# Check database health
health = await DatabaseHealthCheck(db_connection).get_database_info()

# Monitor connection pool
pool_info = await health.get_pool_info()

# Database statistics
stats = await health.get_database_statistics()
```

### Backup Strategy
```python
# Create backup
backup_file = await setup.backup_database("backup_20240101.sql")

# Restore from backup
await setup.restore_database("backup_20240101.sql")
```

### Maintenance Tasks
- **Index optimization**: Regularly analyze and optimize indexes
- **Statistics updates**: Refresh database statistics for query planning
- **Connection pool monitoring**: Track pool usage and adjust sizes
- **Session cleanup**: Monitor and clean expired sessions

## Security Considerations

### Authentication
- **Password hashing**: SHA-256 (configurable to bcrypt)
- **LDAP integration**: Support for corporate directory services
- **Session management**: Secure session handling

### Data Protection
- **Input validation**: All data validated before storage
- **SQL injection protection**: Parameterized queries
- **Access control**: User-based permissions

### Privacy Features
- **Data retention**: Configurable data retention policies
- **User deletion**: Cascade deletion of user data
- **Audit logging**: Track data changes

## Configuration Options

### Database Connection
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=prompt_training_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

### Pool Settings
```env
POSTGRES_MIN_CONNECTIONS=5
POSTGRES_MAX_CONNECTIONS=20
POSTGRES_COMMAND_TIMEOUT=30.0
```

### Batch Processing
```env
BATCH_FLUSH_THRESHOLD=5
SESSION_TIMEOUT_SECONDS=7200
```

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check PostgreSQL service status and credentials
2. **Permission Denied**: Ensure user has necessary database permissions
3. **Timeout Errors**: Adjust connection timeout settings
4. **Pool Exhaustion**: Increase pool size or optimize queries

### Debug Tools

```python
# Test connection
if await test_database_connection():
    print("Database connection OK")

# Check session status
session_info = await batch_manager.get_session_info(ldap_id)

# View active sessions
all_sessions = await batch_manager.get_all_sessions_info()
```

This implementation provides a robust, scalable foundation for the prompt training application while maintaining compatibility with existing workflows and providing migration support.
