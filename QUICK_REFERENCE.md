# 🚀 Quick Reference Guide

## Essential Commands

### Virtual Environment

```bash
# Create
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Deactivate
deactivate
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install specific package
pip install google-adk
pip install streamlit

# Update pip
pip install --upgrade pip

# List installed packages
pip list
```

### Google Cloud

```bash
# Login
gcloud auth login

# Set project
gcloud config set project PROJECT_ID

# Application Default Credentials
gcloud auth application-default login

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# List enabled services
gcloud services list --enabled

# Check current project
gcloud config get-value project
```

### Running the App

```bash
# Start Streamlit app
streamlit run streamlit_app.py

# Start on different port
streamlit run streamlit_app.py --server.port 8502

# Start with auto-reload disabled
streamlit run streamlit_app.py --server.runOnSave false
```

## File Structure

```
prompt-training-app/
├── prompt_training_app.py       # Main application logic
├── streamlit_app.py             # Streamlit UI
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (don't commit!)
├── .env.example                # Environment template
├── README.md                    # Full documentation
├── SETUP_GUIDE.md              # Setup instructions
├── user_progress.json          # User data (auto-generated)
└── .venv/                      # Virtual environment (don't commit!)
```

## Environment Variables

### For Vertex AI
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### For Google AI Studio
```bash
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key
```

## Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Module not found | `pip install -r requirements.txt` |
| Auth error | `gcloud auth application-default login` |
| Port in use | Add `--server.port 8502` |
| Slow responses | First run is slow; subsequent runs faster |
| JSON parse error | Retry submission; app has fallback handling |

## Scoring System

| Category | Max Points | Description |
|----------|------------|-------------|
| Clarity | 25 | Clear and unambiguous |
| Specificity | 25 | Enough context and details |
| Structure | 25 | Well-organized formatting |
| Task Alignment | 25 | Matches scenario goal |
| **TOTAL** | **100** | Overall score |

### Score Tiers
- 🌟 **Excellent**: 85-100
- 👍 **Good**: 70-84
- 💪 **Needs Practice**: 0-69

## Badge Requirements

| Badge | Requirement |
|-------|-------------|
| Perfect Score | Achieve 100/100 on any scenario |
| Consistent Performer | 3 attempts with score > 80 |
| Dedicated Learner | Complete 10 practice attempts |
| Advanced Master | 5 advanced scenarios with avg > 85 |

## Skill Levels

| Level | Requirement |
|-------|-------------|
| Beginner | Default starting level |
| Intermediate | Average ≥70 with 3+ attempts |
| Advanced | Average ≥85 with 5+ attempts |

## Scenario Difficulty

### Beginner (3 scenarios)
- Email Summarization (Outlook)
- Document Formatting (Word)
- Meeting Preparation (Teams)

### Intermediate (3 scenarios)
- Data Analysis (Excel)
- Presentation Creation (PowerPoint)
- Cross-Product Workflow (M365)

### Advanced (3 scenarios)
- Strategic Analysis (Business Chat)
- Complex Automation (Power Automate)
- Enterprise Knowledge Synthesis (M365)

## App Navigation

| Page | Description |
|------|-------------|
| Dashboard | Overview, stats, badges |
| Practice Mode | Main training interface |
| Leaderboard | Top performers ranking |
| Progress History | Your past attempts |
| Learning Resources | Best practices guide |

## Key Classes

### PromptEvaluatorAgent
- Evaluates user prompts using Gemini
- Returns structured JSON feedback
- Scores on 4 dimensions

### CopilotScenarioGenerator
- Provides 9 pre-built scenarios
- 3 difficulty levels
- M365 Copilot focused

### UserProgressTracker
- Saves user data to JSON
- Tracks attempts and scores
- Manages badges and leaderboard

## Testing Checklist

- [ ] Can login with username
- [ ] Dashboard loads with stats
- [ ] Can select scenarios
- [ ] Can submit prompts
- [ ] AI evaluation works
- [ ] Scores are calculated correctly
- [ ] Feedback is displayed
- [ ] Progress is saved
- [ ] Leaderboard updates
- [ ] Badges are awarded

## Useful Links

- **Google ADK Docs**: https://google.github.io/adk-docs/
- **Streamlit Docs**: https://docs.streamlit.io
- **Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
- **Google AI Studio**: https://aistudio.google.com
- **GCP Console**: https://console.cloud.google.com

## Default Ports

- Streamlit: `8501`
- ADK Dev UI (if used): `8000`

## File Permissions (Unix/Linux/macOS)

```bash
# Make scripts executable
chmod +x streamlit_app.py
chmod +x prompt_training_app.py
```

## Git Ignore Recommendations

Add to `.gitignore`:
```
.env
.venv/
__pycache__/
*.pyc
user_progress.json
.DS_Store
```

## Quick Test Commands

```bash
# Test Python version
python --version

# Test pip
pip --version

# Test gcloud
gcloud --version

# Test virtual environment is active
which python  # Should show .venv path

# Test imports
python -c "from google.adk.agents import Agent; print('✅ ADK OK')"
python -c "import streamlit; print('✅ Streamlit OK')"

# Test .env loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ .env loaded')"
```

## Support Contacts

- **Technical Issues**: Your AI Engineering Team
- **GCP Billing**: Google Cloud Support
- **API Questions**: Check documentation first

---

## Emergency Commands

### Kill Streamlit if stuck
```bash
# Find process
ps aux | grep streamlit

# Kill by PID
kill -9 <PID>

# Or use pkill
pkill -f streamlit
```

### Reset user progress
```bash
# Backup first
cp user_progress.json user_progress_backup.json

# Remove specific user
# Edit user_progress.json manually

# Reset all data
rm user_progress.json
```

### Clear cache
```bash
# Streamlit cache
streamlit cache clear
```

---

**Keep this reference handy while developing and training!** 📌