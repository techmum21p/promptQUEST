# 🚀 Cursor Setup Guide - Prompt Engineering Training App

This guide will help you set up and run the Prompt Engineering Training App from Cursor or terminal.

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- Git (for version control)

## 🔧 Initial Setup (One-time)

### 1. Clone and Navigate to Project
```bash
cd /Users/airees/Python/promptQUEST
```

### 2. Set Up Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Frontend Dependencies
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Go back to project root
cd ..
```

### 4. Environment Configuration
```bash
# Copy the example environment file
cp env-example.env .env

# Edit .env file and add your Google API key
# GOOGLE_API_KEY=your_api_key_here
```

## 🏃‍♂️ Running the Application

### Method 1: Using the Modern Startup Script
```bash
# Make the script executable
chmod +x start-modern.sh

# Run the application (starts both backend and frontend)
./start-modern.sh
```

### Method 2: Manual Startup (Recommended for Development)

#### Terminal 1 - Backend Server
```bash
# Navigate to project root
cd /Users/airees/Python/promptQUEST

# Activate virtual environment
source venv/bin/activate

# Start backend server
python3 backend/main.py
```
The backend will be available at: `http://localhost:8000`

#### Terminal 2 - Frontend Server
```bash
# Navigate to frontend directory
cd /Users/airees/Python/promptQUEST/frontend

# Start frontend development server
npm run dev
```
The frontend will be available at: `http://localhost:3000`

## 🌐 Accessing the Application

1. **Frontend**: Open your browser and go to `http://localhost:3000`
2. **Backend API**: Available at `http://localhost:8000`
3. **API Documentation**: `http://localhost:8000/docs` (FastAPI auto-generated docs)

## 🔍 Troubleshooting

### Common Issues

#### 1. "python: command not found"
- Use `python3` instead of `python` on macOS/Linux
- Make sure Python 3.8+ is installed

#### 2. "ModuleNotFoundError: No module named 'fastapi'"
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

#### 3. "Port already in use"
- Kill existing processes:
  ```bash
  # Kill backend
  pkill -f "python3 backend/main.py"
  
  # Kill frontend
  pkill -f "next dev"
  ```

#### 4. Frontend not connecting to backend
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify API_BASE_URL in `frontend/lib/api.ts`

### Health Checks

#### Backend Health Check
```bash
curl http://localhost:8000/health
```

#### Frontend Health Check
```bash
curl http://localhost:3000
```

## 📁 Project Structure

```
promptQUEST/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main backend server
│   ├── requirements.txt    # Python dependencies
│   └── user_progress.json  # User data storage
├── frontend/               # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   ├── lib/              # API client and store
│   └── package.json       # Node.js dependencies
├── venv/                  # Python virtual environment
├── user_progress.json     # Main user data file
├── requirements.txt       # Python dependencies
└── start-modern.sh       # Startup script
```

## 🎯 Key Features

- **Practice Mode**: Generate and practice with AI scenarios
- **Leaderboard**: View top performers and rankings
- **Progress Tracking**: Monitor your improvement over time
- **Data Export**: Export your progress data to CSV
- **Admin Panel**: Manage users and view analytics

## 🔄 Development Workflow

1. **Start both servers** (backend + frontend)
2. **Make changes** to code
3. **Hot reload** will automatically update the frontend
4. **Restart backend** if you make changes to Python files
5. **Test changes** in browser at `http://localhost:3000`

## 📝 Useful Commands

```bash
# Check running processes
ps aux | grep python3
ps aux | grep next

# View logs
tail -f backend/logs/app.log  # If logging is enabled

# Reset user data (if needed)
rm user_progress.json
rm backend/user_progress.json

# Update dependencies
pip install -r requirements.txt --upgrade
cd frontend && npm update
```

## 🆘 Getting Help

If you encounter issues:
1. Check this troubleshooting section
2. Verify all prerequisites are installed
3. Ensure virtual environment is activated
4. Check that ports 3000 and 8000 are available
5. Review the console output for error messages

## 🎉 You're Ready!

Once both servers are running, you can:
- Login with any username
- Practice with different difficulty levels
- View your progress and leaderboard
- Export your data for analysis

Happy coding! 🚀
