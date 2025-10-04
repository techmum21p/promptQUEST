# Migration Plan: Streamlit → Next.js + FastAPI + Docker

## Technology Stack
- **Frontend**: Next.js 14 (React 18)
- **Backend**: FastAPI with async PostgreSQL
- **Database**: PostgreSQL (keep existing setup)
- **Containerization**: Docker
- **Authentication**: JWT tokens with FastAPI Security

## Current Application Analysis

### Existing Pages/Components
Based on `streamlit_app_db.py`, your app has:
1. **Authentication**: Login/Registration with LDAP integration
2. **Dashboard**: Overview with quick stats
3. **Practice Mode**: Scenario selection and prompt evaluation
4. **Leaderboard**: User rankings
5. **Progress History**: Individual user progress
6. **Admin Panel**: Administrative functions
7. **Navigation**: Sidebar with page switching

### Current Database Schema
- Users table with LDAP integration
- User progress with detailed scoring
- Badges and achievements
- Leaderboard materialized views

## Implementation Plan

### Phase 1: Backend FastAPI Setup
1. Create FastAPI backend with async database integration
2. Port existing database services (UserService, ProgressService, etc.)
3. Create REST API endpoints for all current functionality
4. Implement JWT authentication

### Phase 2: Frontend Next.js Setup
1. Create Next.js application structure
2. Implement page routing equivalent to current Streamlit pages
3. Create reusable components (Dashboard, PracticeMode, Leaderboard, etc.)
4. Implement modern UI matching current design

### Phase 3: Integration & Containerization
1. Connect frontend to FastAPI backend
2. Create Docker containers for both applications
3. Set up docker-compose for easy deployment
4. Test complete integration

## Benefits of Migration

### Technical Benefits
- ✅ Fixes database connection issues permanently
- ✅ Better async support throughout the stack
- ✅ Improved session management
- ✅ Better error handling and debugging
- ✅ Production-ready scalability

### User Experience Benefits
- ✅ Faster page loads and navigation
- ✅ Better responsive design
- ✅ Improved offline capabilities
- ✅ Modern web app experience

### Development Benefits
- ✅ Better development experience
- ✅ Cleaner code separation
- ✅ Easier testing and debugging
- ✅ Better deployment options

## File Structure
```
promptQUEST-nextjs/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   ├── database/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── styles/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Migration Strategy
1. **Non-disruptive**: Keep current Streamlit app running during migration
2. **Feature parity**: Ensure all current functionality is maintained
3. **Data preservation**: Use existing PostgreSQL database
4. **UI consistency**: Maintain current design and user flows
5. **Testing**: Comprehensive testing before cutover
