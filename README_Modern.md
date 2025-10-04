# 🎯 PromptQuest - Modern Web Application

A modern, containerized version of the Prompt Engineering Training App with Next.js frontend and FastAPI backend.

## 🌟 Architecture

- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and Zustand for state management
- **Backend**: FastAPI with async support and comprehensive API endpoints  
- **AI Integration**: Google Gemini via Google ADK (compatible with both Vertex AI and Google AI Studio)
- **Deployment**: Docker containers with docker-compose for easy local deployment
- **UI**: Modern, responsive design with improved UX/UI over the original Streamlit version

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Google API credentials (see Configuration section)

## 🔧 Configuration

### Required Environment Variables
Create a `.env` file with the following:

```env
# Google AI Configuration
GOOGLE_API_KEY=your-google-ai-studio-api-key

# Optional: Vertex AI Configuration (if you prefer Vertex AI over Google AI Studio)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# LLM Model (optional)
LLM_MODEL=gemini-2.5-flash

# Frontend API URL (for development)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 📁 Project Structure

```
promptquest/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main FastAPI application
│   └── requirements.txt       # Python dependencies
├── frontend/                   # Next.js frontend
│   ├── app/                   # Next.js App Router
│   ├── components/            # React components
│   ├── lib/                   # API client and stores
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.js     # Tailwind CSS config
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile.backend        # Backend Dockerfile
├── Dockerfile.frontend       # Frontend Dockerfile
├── .dockerignore             # Docker ignore file
├── .env.example              # Environment variables template
└── README_Modern.md          # This file
```

## 🚀 Quick Start with Docker

### 1. Clone and Setup
```bash
git clone <your-repo>
cd promptquest
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Google API credentials
```

### 3. Run with Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Stop Services
```bash
docker-compose down
```

## 🎮 Features

### Enhanced User Experience
- **Responsive Design**: Modern, mobile-friendly UI
- **Real-time Updates**: Instant feedback and progress tracking
- **Better Navigation**: Intuitive sidebar navigation
- **Performance**: Faster loading with optimized API calls

### All Original Features Retained
- **Gamification**: Scoring, badges, leaderboard, skill progression
- **AI-Powered Evaluation**: Comprehensive prompt assessment
- **Scenario Generation**: Preset, AI-generated, and mixed scenarios
- **Progress Tracking**: Detailed history and analytics
- **Data Export**: CSV export for analysis
- **Admin Panel**: Data management and system monitoring

### Technical Improvements
- **Modern Architecture**: Separation of frontend/backend concerns
- **Type Safety**: Full TypeScript implementation
- **API-First**: RESTful API for all operations
- **Containerization**: Easy deployment and scaling
- **Better Error Handling**: Comprehensive error management

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Full Stack Development
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: Docker (if testing containerization)
docker-compose up
```

## 📊 API Endpoints

The FastAPI backend provides these main endpoints:

### User Management
- `POST /api/users` - Add new user
- `GET /api/users/{username}/stats` - Get user statistics

### Scenario Management  
- `GET /api/scenarios/levels/{level}` - Get scenarios by difficulty
- `GET /api/scenarios/random/{level}` - Get random preset scenario
- `POST /api/scenarios/generate` - Generate scenario (preset/ai/mixed)
- `GET /api/scenarios/statistics` - Get scenario statistics

### Prompt Evaluation
- `POST /api/evaluate` - Evaluate user prompt

### Progress Tracking
- `POST /api/progress/record` - Record user attempt
- `GET /api/progress/leaderboard` - Get leaderboard
- `GET /api/progress/export-summary` - Get export statistics
- `POST /api/progress/export-csv` - Export data to CSV

### System
- `GET /health` - Health check

Visit http://localhost:8000/docs for interactive API documentation.

## 🚢 Deployment

### Production Considerations
1. **Environment Variables**: Ensure all production secrets are properly set
2. **Data Persistence**: Mount volumes for user_progress.json and CSV exports
3. **Security**: Use HTTPS in production
4. **Monitoring**: Consider adding health checks and logging
5. **Database**: For production scale, consider PostgreSQL instead of JSON files

### Scaling
```bash
# Scale backend containers
docker-compose up --scale backend=3

# Use external database
# Replace JSON file storage with PostgreSQL container
```

## 🔍 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check backend is running on port 8000
   - Verify `NEXT_PUBLIC_API_BASE_URL` matches your setup
   - Check Docker networking if using containers

2. **Google API Errors**
   - Verify `GOOGLE_API_KEY` is valid and active
   - Check API quotas and billing
   - Ensure required APIs are enabled (Gemini API)

3. **Build Failures**
   - Run `docker-compose down` first to clean up
   - Check Docker logs: `docker-compose logs backend` or `frontend`
   - Verify all environment variables are set:

4. **Data Persistence**
   - User data is stored in `user_progress.json` 
   - CSV exports are stored in the project root
   - Ensure proper volume mounts for persistence

### Viewing Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f backend
```

## 🔄 Migration from Streamlit Version

The modern version is designed to be a drop-in replacement for the original Streamlit app:

1. **Data Compatibility**: Uses the same user_progress.json format
2. **Feature Parity**: All original features are preserved
3. **Enhanced UX**: Better performance and modern UI
4. **Deployment**: Easier containerization and scaling

## 📈 Performance Benefits

- **Faster Loading**: Optimized bundle splitting and caching
- **Better UX**: Real-time updates without page refreshes  
- **Scalability**: API-first architecture allows horizontal scaling
- **Maintainability**: Separated concerns between frontend/backend
- **Modern Tooling**: TypeScript, Tailwind, and modern React patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker Compose
5. Submit a pull request

## 📄 License

This project maintains the same license as the original PromptQuest application.

## 🆘 Support

For issues or questions:
1. Check this README and the original documentation
2. Check Docker logs for errors
3. Verify environment configuration
4. Open an issue with your configuration and error logs

---

**Next.js vs React.js**: Next.js was chosen over plain React.js because it provides:
- Built-in routing, API routes, and SSR capabilities
- Better performance optimization
- Easier deployment and scaling
- Modern development experience with App Router
- TypeScript support out of the box

**FastAPI**: Provides async support, automatic API documentation, type validation, and excellent performance - ideal for AI workloads.
