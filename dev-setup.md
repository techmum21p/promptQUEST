# Development Setup Guide

This guide shows how to set up the modern PromptQuest application for local development.

## 🛠️ Development Setup (Without Docker)

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### 1. Clone and Setup
```bash
git clone <your-repo>
cd promptquest
```

### 2. Configure Environment
```bash
cp env-modern.example .env
# Edit .env with your Google API credentials
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy core dependencies
cp ../prompt_training_app.py .
cp ../requirements.txt ../requirements.txt.backup
pip install -r ../requirements.txt

# Start backend
uvicorn main:app --reload --port 8000
```

### 4. Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### 5. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Configuration Details

### Environment Variables Required

```env
# Google AI Studio API Key (Recommended)
GOOGLE_API_KEY=your-api-key-here

# Frontend configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Getting API Credentials

1. **Google AI Studio** (Recommended)
   - Go to https://aistudio.google.com/app/apikey
   - Create a new API key
   - Copy to `GOOGLE_API_KEY` in .env

2. **Vertex AI** (Advanced)
   - Set up Google Cloud Project
   - Enable Vertex AI API
   - Configure authentication
   - Set `GOOGLE_GENAI_USE_VERTEXAI=TRUE` in .env

## 📁 Project Structure

```
promptquest/
├── backend/                # FastAPI backend
│   ├── main.py            # Main application
│   └── requirements.txt   # Dependencies
├── frontend/               # Next.js frontend
│   ├── app/               # App Router
│   ├── components/        # React components
│   ├── lib/               # API client & stores
│   └── package.json       # Node dependencies
├── docker-compose.yml     # Container setup
├── Dockerfile.*           # Container definitions
├── start-modern.sh        # Quick start script
└── README_Modern.md       # Full documentation
```

## 🚀 Quick Commands

### Development
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: With Docker
docker-compose up --build
```

### Useful Development Commands
```bash
# Install frontend dependencies
cd frontend && npm install

# Install backend dependencies
cd backend && pip install -r requirements.txt

# Check frontend types
cd frontend && npm run type-check

# Lint frontend
cd frontend && npm run lint

# Build frontend for production
cd frontend && npm run build
```

## 🔍 Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Copy core modules to backend directory
   cp prompt_training_app.py backend/
   ```

2. **API Connection Issues**
   - Check backend is running on port 8000
   - Verify NEXT_PUBLIC_API_BASE_URL in .env
   - Check browser console for CORS errors

3. **Google API Errors**
   - Verify API key is valid
   - Check API quotas
   - Ensure Gemini API is enabled

4. **Database/Storage Issues**
   - Check user_progress.json permissions
   - Verify backup CSV files can be created

### Debugging

- **Backend logs**: Check terminal running uvicorn
- **Frontend logs**: Check browser dev tools console
- **Network issues**: Check Network tab in browser
- **API issues**: Visit http://localhost:8000/docs

## 📊 Features Comparison

| Feature | Streamlit Version | Modern Version |
|---------|------------------|----------------|
| User Interface | Streamlit UI | Next.js + Tailwind CSS |
| Backend | Synchronous | FastAPI Async |
| Data Storage | JSON files | JSON files (compatible) |
| Deployment | `streamlit run` | Docker Compose |
| Development | Single file | Frontend/Backend separation |
| Type Safety | Limited | Full TypeScript |
| Performance | Streamlit overhead | Optimized React |

## 🎯 Next Steps

1. **Run the application**: Use `./start-modern.sh` or manual setup
2. **Test features**: Try all scenarios, evaluation, data export
3. **Customize**: Modify UI components or add new features
4. **Deploy**: Use Docker Compose for production deployment

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Google ADK](https://ai.google.dev/docs)
- [Docker Compose](https://docs.docker.com/compose/)

## 💡 Tips

- Use browser dev tools to debug frontend issues
- Visit http://localhost:8000/docs for API testing
- Check Docker logs: `docker-compose logs backend`
- Keep .env file secure and never commit it
- Use TypeScript features for better development experience
