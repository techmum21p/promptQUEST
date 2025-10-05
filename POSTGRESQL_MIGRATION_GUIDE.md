# PostgreSQL Migration Guide

This guide explains how to migrate the PromptQUEST application from JSON file storage to PostgreSQL with LDAP ID support.

## Overview

The application has been updated to use PostgreSQL as the primary data store instead of JSON files. This provides:

- **Better performance** for large datasets
- **Data integrity** with ACID transactions
- **Scalability** for multiple users
- **LDAP ID integration** for enterprise authentication
- **Concurrent access** support

## Database Schema

### Users Table
- `ldap_id` (Primary Key): Unique LDAP identifier
- `username`: Display name
- `total_score`: Cumulative score
- `attempts`: Number of attempts
- `skill_level`: Current skill level
- `badges`: JSON array of earned badges
- `created_at`, `updated_at`: Timestamps

### User Attempts Table
- `id` (Primary Key): UUID for each attempt
- `ldap_id` (Foreign Key): References users.ldap_id
- `scenario_id`: Scenario identifier
- `score`: Attempt score
- `user_prompt`: User's prompt text
- `timestamp`: When attempt was made
- Evaluation scores: `clarity_score`, `specificity_score`, `structure_score`, `task_alignment_score`
- `feedback`: AI feedback text
- `strengths`, `improvements`: JSON arrays

### Leaderboard Table
- Cached leaderboard data for performance
- Updated automatically when new attempts are recorded

## Setup Instructions

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql postgresql-server
sudo systemctl start postgresql
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Set Up Database

Run the setup script:
```bash
./setup_postgres.sh
```

Or manually:
```bash
createdb promptquest
```

### 4. Configure Environment

Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/promptquest
GOOGLE_API_KEY=your_google_api_key_here
```

### 5. Migrate Existing Data

**Option A: Automatic Migration (with placeholder LDAP IDs)**
```bash
python migrate_to_postgres.py ../user_progress.json
```

**Option B: Interactive Migration (with custom LDAP IDs)**
```bash
python migrate_to_postgres.py ../user_progress.json --interactive
```

### 6. Start the Application

```bash
python main.py
```

## API Changes

### Updated Endpoints

**Add User:**
```json
POST /api/users
{
  "ldap_id": "user123",
  "username": "john.doe"
}
```

**Get User Stats:**
```
GET /api/users/{ldap_id}/stats
```

**Record Attempt:**
```json
POST /api/progress/record
{
  "ldap_id": "user123",
  "scenario_id": "b1",
  "user_prompt": "Create a summary...",
  "evaluation": {
    "total_score": 85,
    "clarity_score": 20,
    "specificity_score": 18,
    "structure_score": 22,
    "task_alignment_score": 25,
    "feedback": "Good prompt...",
    "strengths": ["Clear objective"],
    "improvements": ["Add more context"]
  }
}
```

## Frontend Updates Needed

The frontend will need to be updated to:

1. **Collect LDAP IDs** during user registration/login
2. **Use LDAP IDs** instead of usernames for API calls
3. **Handle LDAP authentication** if integrating with enterprise systems

### Example Frontend Changes

**User Registration:**
```typescript
const addUser = async (ldapId: string, username: string) => {
  const response = await fetch('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ldap_id: ldapId, username })
  });
  return response.json();
};
```

**Record Attempt:**
```typescript
const recordAttempt = async (ldapId: string, scenarioId: string, userPrompt: string, evaluation: any) => {
  const response = await fetch('/api/progress/record', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ldap_id: ldapId,
      scenario_id: scenarioId,
      user_prompt: userPrompt,
      evaluation
    })
  });
  return response.json();
};
```

## Troubleshooting

### Common Issues

**1. Database Connection Error**
- Check if PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in .env file
- Ensure database exists: `psql -l`

**2. Migration Errors**
- Check JSON file format
- Verify database permissions
- Review migration script output

**3. LDAP ID Conflicts**
- Use unique LDAP IDs for each user
- Check for existing users before migration

### Useful Commands

```bash
# Check database connection
psql $DATABASE_URL -c "SELECT version();"

# View tables
psql $DATABASE_URL -c "\dt"

# Check user data
psql $DATABASE_URL -c "SELECT ldap_id, username, total_score FROM users;"

# Export data
python -c "from postgres_tracker import PostgreSQLUserProgressTracker; t = PostgreSQLUserProgressTracker(); print(t.export_to_csv())"
```

## Performance Considerations

- **Indexes**: The schema includes indexes on frequently queried fields
- **Leaderboard Caching**: Leaderboard data is cached for better performance
- **Connection Pooling**: Consider using connection pooling for production
- **Backup Strategy**: Implement regular database backups

## Security Considerations

- **LDAP Integration**: Integrate with your organization's LDAP system
- **Database Security**: Use strong passwords and restrict database access
- **Environment Variables**: Keep sensitive data in environment variables
- **Input Validation**: All inputs are validated through Pydantic models

## Rollback Plan

If you need to rollback to JSON storage:

1. Export current data: `python -c "from postgres_tracker import PostgreSQLUserProgressTracker; t = PostgreSQLUserProgressTracker(); t.export_to_csv('rollback_data.csv')"`
2. Revert to old main.py (backup the PostgreSQL version)
3. Restore user_progress.json from backup

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the migration script output
3. Verify database connectivity and permissions
4. Check application logs for detailed error messages
