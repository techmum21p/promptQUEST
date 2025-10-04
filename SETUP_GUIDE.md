# 🚀 Complete Setup Guide - Step by Step

This guide walks you through setting up the Prompt Engineering Training App from scratch.

## 📁 Step 1: Create Project Structure

```bash
# Create project directory
mkdir prompt-training-app
cd prompt-training-app

# Create Python files
touch prompt_training_app.py
touch streamlit_app.py
touch requirements.txt
touch .env.example
touch README.md
```

Your directory should look like this:
```
prompt-training-app/
├── prompt_training_app.py    # Main app with Google ADK agents
├── streamlit_app.py           # Streamlit UI
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── .env                      # Your actual credentials (create next)
└── README.md                 # Documentation
```

## 📝 Step 2: Copy the Code Files

Copy the code I provided into each file:

1. **prompt_training_app.py** - The main application with:
   - `PromptEvaluatorAgent` class
   - `CopilotScenarioGenerator` class
   - `UserProgressTracker` class
   - Helper functions

2. **streamlit_app.py** - The Streamlit UI with:
   - Login page
   - Dashboard
   - Practice mode
   - Leaderboard
   - Progress history
   - Learning resources

3. **requirements.txt** - All Python dependencies

4. **.env.example** - Template for environment variables

5. **README.md** - Complete documentation

## 🐍 Step 3: Set Up Python Environment

```bash
# Check Python version (need 3.9+)
python --version

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Verify activation (you should see (.venv) in your prompt)
```

## 📦 Step 4: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep google-adk
pip list | grep streamlit
```

Expected packages:
- google-adk (>= 0.2.0)
- streamlit (>= 1.28.0)
- google-cloud-aiplatform (>= 1.38.0)
- google-genai (>= 0.2.0)
- python-dotenv (>= 1.0.0)

## ☁️ Step 5: Set Up Google Cloud (Choose One Method)

### Method A: Vertex AI (Recommended for Production)

#### 5A.1: Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click "Create Project" or select existing project
3. Note your Project ID (you'll need this)

#### 5A.2: Enable Required APIs

```bash
# Install gcloud CLI if not already installed
# Download from: https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Verify API is enabled
gcloud services list --enabled | grep aiplatform
```

#### 5A.3: Set Up Authentication

```bash
# Set up Application Default Credentials
gcloud auth application-default login

# This will open a browser for authentication
# Follow the prompts to authenticate
```

#### 5A.4: Create .env File

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Add this content to `.env`:
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-actual-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

Replace `your-actual-project-id` with your actual GCP project ID.

### Method B: Google AI Studio (For Quick Testing)

#### 5B.1: Get API Key

1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the generated key

#### 5B.2: Create .env File

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Add this content to `.env`:
```bash
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-actual-api-key-here
```

Replace `your-actual-api-key-here` with your actual API key.

## ✅ Step 6: Verify Setup

### Test Google ADK Installation

Create a test file `test_adk.py`:

```python
from google.adk.agents import Agent
from dotenv import load_dotenv

load_dotenv()

# Create a simple test agent
test_agent = Agent(
    name="test_agent",
    model="gemini-2.0-flash",
    description="Test agent",
    instruction="You are a helpful assistant."
)

print("✅ Google ADK setup successful!")
print(f"Agent name: {test_agent.name}")
print(f"Model: {test_agent.model}")
```

Run the test:
```bash
python test_adk.py
```

If successful, you should see:
```
✅ Google ADK setup successful!
Agent name: test_agent
Model: gemini-2.0-flash
```

### Test Streamlit Installation

```bash
streamlit hello
```

This should open a Streamlit demo in your browser. Close it when done.

## 🎮 Step 7: Run the Application

```bash
# Make sure you're in the project directory with virtual environment activated
streamlit run streamlit_app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Your browser should automatically open to the app. If not, manually open http://localhost:8501

## 🎯 Step 8: Test the Application

1. **Login Page**
   - Enter a username (e.g., "test_user")
   - Click "Start Training"

2. **Dashboard**
   - Verify you see your stats (all zeros initially)
   - Check the sidebar navigation

3. **Practice Mode**
   - Select "beginner" difficulty
   - Click "Get Random Scenario"
   - Read the scenario
   - Write a simple prompt
   - Click "Submit for Evaluation"
   - Wait for AI evaluation (this may take 10-30 seconds on first run)

4. **Check Results**
   - Verify you get a score (0-100)
   - Review the detailed feedback
   - Check that your attempt is recorded

5. **Leaderboard**
   - Navigate to Leaderboard in sidebar
   - Verify your username appears

## 🐛 Troubleshooting Setup Issues

### Issue: "Module not found: google.adk"

**Solution:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "Permission denied" when running streamlit

**Solution:**
```bash
# On macOS/Linux, you may need to make the file executable
chmod +x streamlit_app.py

# Or try running with python directly
python -m streamlit run streamlit_app.py
```

### Issue: "Port 8501 already in use"

**Solution:**
```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502
```

### Issue: Authentication errors with Vertex AI

**Solution:**
```bash
# Re-authenticate
gcloud auth application-default login

# Verify your project is set correctly
gcloud config get-value project

# Check if API is enabled
gcloud services list --enabled | grep aiplatform
```

### Issue: "Invalid API Key" with Google AI Studio

**Solution:**
- Verify your API key is correct in `.env`
- Check that you copied the entire key
- Ensure no extra spaces or quotes
- Try generating a new API key

### Issue: Slow evaluation responses

**Solution:**
- First run is always slower (cold start)
- Check your internet connection
- Consider using a closer region (if using Vertex AI)
- For production, consider using Cloud Run

## 📊 Verify Complete Setup Checklist

- [ ] Project directory created
- [ ] All code files in place
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Google Cloud project created (if using Vertex AI)
- [ ] APIs enabled (if using Vertex AI)
- [ ] Authentication configured
- [ ] `.env` file created with correct credentials
- [ ] Test agent runs successfully
- [ ] Streamlit starts without errors
- [ ] Can log in to the app
- [ ] Can load scenarios
- [ ] Can submit prompts for evaluation
- [ ] Receive AI-generated feedback
- [ ] Progress is saved and displayed

## 🎓 Next Steps After Setup

1. **Familiarize Yourself**
   - Complete a few practice scenarios
   - Explore all the pages
   - Check the learning resources

2. **Customize for Your Team**
   - Add company-specific scenarios
   - Adjust evaluation criteria if needed
   - Modify branding/colors

3. **Train Your Team**
   - Schedule training sessions
   - Share login instructions
   - Set up friendly competitions

4. **Monitor Usage**
   - Check `user_progress.json` for engagement
   - Review leaderboard regularly
   - Gather feedback from users

## 💡 Tips for Success

1. **Start Simple**: Test with Google AI Studio first before using Vertex AI
2. **Iterate**: The app is designed to be customized - make it yours!
3. **Engage Users**: Use the leaderboard and badges to drive engagement
4. **Share Best Practices**: Use the learning resources page to share tips
5. **Monitor Costs**: If using Vertex AI, set up billing alerts

## 📞 Getting Additional Help

If you encounter issues not covered here:

1. **Google ADK Documentation**: https://google.github.io/adk-docs/
2. **Streamlit Docs**: https://docs.streamlit.io
3. **Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
4. **Google Cloud Support**: https://cloud.google.com/support

---

**Setup Complete! 🎉**

You're now ready to start training your team in prompt engineering for Microsoft 365 Copilot!