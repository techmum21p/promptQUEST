# Prompt Training App - Database Version

A PostgreSQL-backed implementation of the Prompt Training App with advanced user management, progress tracking, and analytics capabilities.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-db.txt
```

### 2. Setup PostgreSQL Database
```bash
# Copy environment file
cp env-example-db.env .env
# Edit .env with your PostgreSQL credentials

# Setup database
python database/setup.py --action setup

# Verify setup
python database/setup.py --action verify
```

### 3. Run migration from JSON/CSV (Optional)
```bash
# If migrating from existing data
python migrate_from_json.py
```

### 4. Start the Application
```bash
streamlit run streamlit_app_db.py
```

### 5. Test Integration
```bash
# Quick test
python test_database_integration.py quick

# Comprehensive test
python test_database_integration.py
```

## 📊 Key Features

### 🎯 **Advanced User Management**
- **LDAP Integration**: Corporate directory service support
- **Role-based Groups**: Department-level organization (Engineering, Product, Marketing, etc.)
- **Secure Authentication**: Password hashing and session management
- **User Profiles**: Comprehensive user statistics and progress tracking

### 📈 **Intelligent Progress Tracking**
- **Detailed Scoring**: Breakdown by clarity, specificity, structure, and task alignment
- **Real-time Analytics**: Live progress updates and performance metrics
- **Skill Progression**: Automatic skill level assessment (Beginner → Intermediate → Advanced)
- **Historical Data**: Complete attempt history and performance trends

### 🏆 **Badge & Achievement System**
- **Perfect Score**: Achieve 100 points on any attempt
- **Consistent Performer**: Average >80 with ≥3 attempts
- **Dedicated Learner**: Complete ≥10 attempts
- **Advanced Master**: Excel on advanced scenarios (avg >85, ≥5 attempts)

### 🚀 **Performance Optimizations**
- **Batch Processing**: Efficient bulk operations (every 5 attempts)
- **Session Management**: Smart session-based data caching
- **Connection Pooling**: Optimized database connections
- **Materialized Views**: Pre-computed leaderboard for speed

### 📊 **Advanced Analytics**
- **Real-time Leaderboard**: Ranked by performance
- **Group-based Rankings**: Department-level competition
- **Scenario Analytics**: Performance metrics per scenario type
- **Progress Dashboards**: Comprehensive user statistics

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  App Services   │────│   PostgreSQL   │
│                 │    │                 │    │                 │
│ • Authentication│    │ • User Mgmt     │    │ • Users Table   │
│ • Training      │    │ • Progress      │    │ • Progress     │
│ • Analytics     │    │ • Badges        │    │ • Badges       │
│ • Leaderboard   │    │ • Batch Ops     │    │ • Leaderboard  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
promptQUEST/
├── database/                          # Database core
│   ├── schema.sql                     # Database schema
│   ├── config.py                     # Connection management
│   ├── service.py                    # CRUD operations
│   ├── setup.py                      # Setup utilities
│   └── migrations/                   # Database migrations
├── prompt_training_app_db.py          # Main application
├── streamlit_app_db.py               # UI with database
├── batch_manager.py                  # Session management
├── test_database_integration.py      # Test suite
├── env-example-db.env                # Environment template
├── requirements-db.txt               # Dependencies
├── DATABASE_IMPLEMENTATION.md        # Technical documentation
└── README_DATABASE_VERSION.md        # This file
```

## 🎮 Usage Examples

### User Registration & Authentication
```python
tracker = UserProgressTrackerDB()

# Register new user
user = await tracker.register_user(
    ldap_id="john.doe",
    username="John Doe", 
    password="secure123",
    email="john@company.com",
    group="Engineering"
)

# Authenticate user
authenticated_user = await tracker.authenticate_user("john.doe", "secure123")
```

### Progress Tracking with Batch Processing
```python
# Record attempt (automatically batched)
evaluation = {
    "total_score": 92,
    "clarity_score": 23,
    "specificity_score": 23,
    "structure_score": 23,
    "task_alignment_score": 23,
    "feedback": "Excellent prompt!",
    "strengths": ["Clear objective", "Specific context"],
    "improvements": ["Consider adding examples"]
}

await tracker.record_attempt("john.doe", "b1", 92, evaluation, user_prompt)
```

### Advanced Analytics
```python
# Get user statistics
stats = await tracker.get_user_data("john.doe")
# Returns: attempt_count, avg_score, skill_level, badges, etc.

# Get leaderboard
leaderboard = await tracker.get_leaderboard(top_n=10, group="Engineering")

# Get scenario performance
scenario_stats = await progress_service.get_scenario_performance("b1")
```

## 🔧 Configuration Options

### Environment Variables (.env)
```env
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=prompt_training_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Connection Pool Settings
POSTGRES_MIN_CONNECTIONS=5
POSTGRES_MAX_CONNECTIONS=20
POSTGRES_COMMAND_TIMEOUT=30.0

# Batch Processing
BATCH_FLUSH_THRESHOLD=5
SESSION_TIMEOUT_SECONDS=7200

# AI Model Configuration
LLM_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=your_api_key
```

## 📊 Database Schema Highlights

### Users Table
- **ldap_id**: Corporate LDAP identifier
- **user_group**: Department/organization
- **password_hash**: Secure password storage
- **last_login**: Authentication tracking

### Progress Table
- **attempt_number**: Sequential attempt tracking
- **score_breakdown**: Detailed scoring (25 points each dimension)
- **session_id**: Batch processing support
- **strengths/improvements**: Arrays for structured feedback

### Badges Table
- **badge_name**: Achievement identification
- **scenario_id**: Context of award
- **awarded_at**: Timestamp tracking

## 🔍 Monitoring & Maintenance

### Health Checks
```python
# Database health
from database.config import DatabaseHealthCheck
health = DatabaseHealthCheck(db_connection)
info = await health.get_database_info()

# Session monitoring
session_info = await batch_manager.get_session_info(user_ldap_id)
```

### Performance Monitoring
```python
# Connection pool status
pool_info = await health.get_pool_info()

# Database statistics
stats = await health.get_full_statistics()
```

## 🚨 Troubleshooting

### Common Issues

**Connection Errors**
```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d prompt_training_db

# Check service status
sudo systemctl status postgresql
```

**Permission Issues**
```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE prompt_training_db TO your_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
```

**Session Problems**
```python
# Force flush all sessions
results = await batch_manager.force_flush_all_sessions()
```

## 🎯 Migration from JSON/CSV

### Preparation
1. Export existing data using CSV export function
2. Update CSV files to include LDAP IDs for users
3. Ensure group assignments are consistent

### Migration Process
```python
# Custom migration script (example)
await migrate_from_csv("user_progress_export_20240101.csv")
```

## 🔒 Security Features

### Authentication
- **Password Hashing**: SHA-256 with bcrypt option
- **Session Management**: Secure session handling
- **LDAP Integration**: Corporate directory support

### Data Protection
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Parameterized queries
- **Access Control**: User-based permissions

## 📈 Performance Benefits

### Before (JSON/CSV)
- ❌ File I/O bottlenecks
- ❌ Limited concurrent access
- ❌ No reliable transactions
- ❌ Manual backup procedures
- ❌ No real-time analytics

### After (PostgreSQL)
- ✅ Concurrent access support
- ✅ ACID transaction guarantees
- ✅ Automatic backup tools
- ✅ Real-time analytics
- ✅ Optimized query performance
- ✅ Scalable architecture

## 🎉 Benefits Summary

### For Users
- **Persistent Progress**: Never lose training data
- **Real-time Badges**: Immediate achievement recognition
- **Advanced Analytics**: Detailed performance insights
- **Leaderboard Competition**: Engage with colleagues
- **Session Continuity**: Pick up where you left off

### For Organizations
- **Department Analytics**: Track training across groups
- **Scalable Infrastructure**: Handle growing user bases
- **Data Integration**: Easy export and reporting
- **Audit Trail**: Complete activity tracking
- **Performance Monitoring**: System health insights

### For Administrators
- **Easy Setup**: Automated database initialization
- **Migration Support**: Seamless JSON/CSV migration
- **Health Monitoring**: Comprehensive system monitoring
- **Backup Management**: Built-in backup utilities
- **Maintenance Tools**: Automated cleanup and optimization

## 🚀 Next Steps

1. **Deploy**: Use the database version for production
2. **Monitor**: Set up health checks and monitoring
3. **Optimize**: Adjust batch sizes and connection pools based on usage
4. **Scale**: Consider read replicas for high-traffic scenarios
5. **Integrate**: Add LDAP/SSO for corporate environments

This database implementation provides a robust, scalable foundation for enterprise prompt training while maintaining the gamification and competition elements that make learning engaging.
