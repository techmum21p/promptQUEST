# 🔧 Troubleshooting Guide

This guide covers common issues and their solutions.

## 📑 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Authentication Issues](#authentication-issues)
3. [Runtime Errors](#runtime-errors)
4. [Performance Issues](#performance-issues)
5. [UI/Display Issues](#uidisplay-issues)
6. [Data Issues](#data-issues)

---

## Installation Issues

### ❌ "Module not found: google.adk"

**Symptoms:**
```
ImportError: No module named 'google.adk'
```

**Solutions:**

1. **Verify virtual environment is activated:**
   ```bash
   # You should see (.venv) in your prompt
   # If not, activate it:
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Check Python version:**
   ```bash
   python --version  # Must be 3.9+
   ```

4. **Install google-adk directly:**
   ```bash
   pip install google-adk
   ```

### ❌ "Command 'pip' not found"

**Solution:**
```bash
# Try python3 and pip3
python3 -m pip install -r requirements.txt
```

### ❌ "Permission denied" during pip install

**Solutions:**

1. **Use virtual environment (recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Use --user flag (not recommended):**
   ```bash
   pip install --user -r requirements.txt
   ```

### ❌ Dependencies installation fails

**Solution:**
```bash
# Clear pip cache and retry
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

---

## Authentication Issues

### ❌ "Could not authenticate with Vertex AI"

**Symptoms:**
```
google.auth.exceptions.DefaultCredentialsError
```

**Solutions:**

1. **Run authentication command:**
   ```bash
   gcloud auth application-default login
   ```

2. **Verify project is set:**
   ```bash
   gcloud config get-value project
   # Should return your project ID
   ```

3. **Check .env file:**
   ```bash
   # Ensure these are set correctly:
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

4. **Verify API is enabled:**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

### ❌ "Invalid API Key" (Google AI Studio)

**Solutions:**

1. **Regenerate API key:**
   - Go to https://aistudio.google.com/apikey
   - Create new API key
   - Update .env file

2. **Check .env format:**
   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your-key-here
   # No quotes, no extra spaces
   ```

3. **Verify API key permissions:**
   - Make sure the API key has Generative Language API access

### ❌ "Quota exceeded" or "Rate limit"

**Solutions:**

1. **Wait a few minutes** - Rate limits reset quickly

2. **Check billing** in Google Cloud Console

3. **Request quota increase** in Google Cloud Console

---

## Runtime Errors

### ❌ "JSON Decode Error"

**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting value
```

**Causes:**
- AI response not in expected format
- Network interruption

**Solutions:**

1. **Retry the submission** - The app has fallback handling

2. **Check your internet connection**

3. **If persistent, check model availability:**
   ```bash
   gcloud ai models list --region=us-central1
   ```

### ❌ "Event loop is closed"

**Symptoms:**
```
RuntimeError: Event loop is closed
```

**Solution:**
```bash
# Restart Streamlit
# Press Ctrl+C to stop
# Run again:
streamlit run streamlit_app.py
```

### ❌ "Address already in use" / Port 8501 occupied

**Solutions:**

1. **Use different port:**
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

2. **Kill existing process:**
   ```bash
   # On macOS/Linux:
   lsof -ti:8501 | xargs kill -9
   
   # On Windows:
   netstat -ano | findstr :8501
   taskkill /PID <PID> /F
   ```

### ❌ "Agent not found in dropdown" (ADK Dev UI)

**Solution:**
- Ensure you're running `adk web` from the **parent** directory of your agent folder
- Check that `__init__.py` exists in your agent folder

### ❌ Import errors from prompt_training_app

**Symptoms:**
```
ImportError: cannot import name 'PromptEvaluatorAgent'
```

**Solutions:**

1. **Check file exists:**
   ```bash
   ls -la prompt_training_app.py
   ```

2. **Verify no syntax errors:**
   ```bash
   python -m py_compile prompt_training_app.py
   ```

3. **Check file encoding** (should be UTF-8)

---

## Performance Issues

### 🐌 Evaluation takes too long (>60 seconds)

**Solutions:**

1. **First run is always slower** (cold start) - subsequent runs are faster

2. **Check internet connection**

3. **Try different region** (in .env):
   ```bash
   GOOGLE_CLOUD_LOCATION=us-east1
   # or
   GOOGLE_CLOUD_LOCATION=europe-west1
   ```

4. **Consider using faster model** (though less powerful):
   ```python
   # In prompt_training_app.py, change model to:
   model="gemini-1.5-flash"
   ```

### 🐌 Streamlit app is slow

**Solutions:**

1. **Clear Streamlit cache:**
   ```bash
   streamlit cache clear
   ```

2. **Disable auto-reload:**
   ```bash
   streamlit run streamlit_app.py --server.runOnSave false
   ```

3. **Check system resources:**
   ```bash
   # CPU and memory usage
   top  # macOS/Linux
   # Task Manager on Windows
   ```

---

## UI/Display Issues

### 📺 Streamlit page won't load

**Solutions:**

1. **Check terminal for errors**

2. **Try different browser** (Chrome recommended)

3. **Clear browser cache**

4. **Check firewall** - allow port 8501

5. **Try different port:**
   ```bash
   streamlit run streamlit_app.py --server.port 8080
   ```

### 📺 Styles not displaying correctly

**Solution:**
```bash
# Force reload (Ctrl+F5 or Cmd+Shift+R)
# Or clear browser cache
```

### 📺 Dashboard shows wrong data

**Solutions:**

1. **Logout and login again**

2. **Check user_progress.json** for corruption:
   ```bash
   python -m json.tool user_progress.json
   ```

3. **If corrupted, backup and reset:**
   ```bash
   mv user_progress.json user_progress_backup.json
   ```

---

## Data Issues

### 💾 Progress not saving

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la user_progress.json
   ```

2. **Check disk space:**
   ```bash
   df -h  # macOS/Linux
   ```

3. **Verify file is not read-only**

### 💾 user_progress.json is corrupted

**Symptoms:**
```
json.decoder.JSONDecodeError
```

**Solutions:**

1. **Backup current file:**
   ```bash
   cp user_progress.json user_progress_corrupted.json
   ```

2. **Try to repair:**
   ```bash
   # View file
   cat user_progress.json
   
   # If JSON is malformed, manually fix or reset
   ```

3. **Reset (last resort):**
   ```bash
   rm user_progress.json
   # File will be recreated on next run
   ```

### 💾 Leaderboard not updating

**Solution:**
```bash
# Force recalculation by:
# 1. Complete one more scenario
# 2. Or delete and let it recreate:
rm user_progress.json
```

---

## Advanced Troubleshooting

### 🔍 Enable Debug Mode

**For Streamlit:**
```bash
streamlit run streamlit_app.py --logger.level=debug
```

**For Python logging:**
Add to beginning of prompt_training_app.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 🔍 Check ADK Version

```bash
pip show google-adk
```

### 🔍 Test Network Connectivity to Google APIs

```bash
# Test Vertex AI endpoint
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT/locations/us-central1/publishers/google/models/gemini-2.0-flash

# Test Google AI Studio
curl https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY
```

### 🔍 Verify Environment Variables are Loading

Create test file `test_env.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

print("GOOGLE_GENAI_USE_VERTEXAI:", os.getenv("GOOGLE_GENAI_USE_VERTEXAI"))
print("GOOGLE_CLOUD_PROJECT:", os.getenv("GOOGLE_CLOUD_PROJECT"))
print("GOOGLE_CLOUD_LOCATION:", os.getenv("GOOGLE_CLOUD_LOCATION"))
print("GOOGLE_API_KEY:", "SET" if os.getenv("GOOGLE_API_KEY") else "NOT SET")
```

Run:
```bash
python test_env.py
```

---

## 🆘 Still Having Issues?

### Check These Resources:

1. **Run setup verification:**
   ```bash
   python test_setup.py
   ```

2. **Review documentation:**
   - README.md
   - SETUP_GUIDE.md
   - QUICK_REFERENCE.md

3. **Check official docs:**
   - [Google ADK](https://google.github.io/adk-docs/)
   - [Streamlit](https://docs.streamlit.io)
   - [Vertex AI](https://cloud.google.com/vertex-ai/docs)

4. **Common error patterns:**

| Error Message | Quick Fix |
|---------------|-----------|
| "No module named..." | `pip install -r requirements.txt` |
| "DefaultCredentialsError" | `gcloud auth application-default login` |
| "Port already in use" | Use `--server.port 8502` |
| "JSON decode error" | Retry submission |
| "Permission denied" | Check file permissions / Use venv |

---

## 📋 Diagnostic Checklist

Before asking for help, verify:

- [ ] Python 3.9+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] .env file exists and configured
- [ ] Authentication completed
- [ ] APIs enabled (if using Vertex AI)
- [ ] test_setup.py passes all tests
- [ ] Internet connection working
- [ ] No firewall blocking
- [ ] Sufficient disk space
- [ ] Latest code from artifacts

---

## 🔄 Complete Reset (Nuclear Option)

If nothing works, start fresh:

```bash
# 1. Backup your data
cp user_progress.json user_progress_backup.json
cp .env .env.backup

# 2. Remove everything
deactivate  # Exit venv
rm -rf .venv
rm user_progress.json

# 3. Start over
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Reconfigure
cp .env.backup .env
gcloud auth application-default login

# 5. Test
python test_setup.py

# 6. Run
streamlit run streamlit_app.py
```

---

**Remember**: Most issues are solved by:
1. Activating virtual environment
2. Reinstalling dependencies
3. Checking .env configuration
4. Re-authenticating with Google Cloud

Good luck! 🍀