# Gemini Setup Guide for PromptQuest

This guide will help you set up PromptQuest with Google AI Studio (the default and recommended method). Vertex AI is also supported as an alternative option.

## 🚀 Quick Setup (5 minutes)

### 1. Get Your API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API key" in the top right
4. Create a new API key or use an existing one
5. Copy the API key (starts with `AIza...`)

### 2. Configure Environment
1. Copy the example environment file:
   ```bash
   cp env-example.env .env
   ```

2. Edit the `.env` file and replace `your-api-key-here` with your actual API key:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=AIzaSy_YOUR_ACTUAL_API_KEY_HERE
   LLM_MODEL=gemini-1.5-flash
   ```

   **Note:** Google AI Studio is the default authentication method. The app will automatically use your API key for authentication.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Test Configuration
```bash
python test_gemini_config.py
```

If successful, you should see:
```
✅ Success! Model Response:
   Gemini API works! Your Google AI Studio configuration is working correctly.
```

### 5. Run the App
```bash
streamlit run streamlit_app.py
```

## 🔧 Troubleshooting

### Common Issues

**❌ "GOOGLE_API_KEY environment variable is required"**
- Make sure you created the `.env` file
- Check that `GOOGLE_API_KEY=your-actual-key` is set correctly
- Ensure there are no quotes around your API key

**❌ "Module not found" errors**
- Run `pip install -r requirements.txt`
- Make sure you uninstalled old heavy dependencies:
  ```bash
  pip uninstall google-cloud-aiplatform google-cloud-automl google-cloud-discovery-engine google-cloud-documentai google-cloud-language google-cloud-speech google-cloud-tasks google-cloud-texttospeech google-cloud-translate google-cloud-videointelligence google-cloud-vision
  ```

**❌ API Key Invalid**
- Double-check your API key from Google AI Studio
- Make sure you haven't exceeded your quota
- Try creating a new API key

**❌ "403 Forbidden" or similar API errors**
- Check your Google AI Studio account billing
- Verify your API key has proper permissions
- Make sure billing is enabled on your Google Cloud project (if AI Studio tracks usage)

### Models Available

The app supports these Gemini models:
- `gemini-1-moment-1.5-flash` (recommended - fast)
- `gemini-1.5-pro` (recommended - high quality) 
- `gemini-1.5-flash` (fastest, baseline quality)
- `gemini-2.0-flash-exp` (experimental)

Change the model by updating `LLM_MODEL` in your `.env` file.

## 💰 Cost Considerations

Google AI Studio has generous free tiers:
- **Free tier**: 150 requests/minute, 15 requests/minute per user
- **Pay-as-you-go**: Starts at $0.00025 per 1K input tokens

This app typically uses ~500-1000 tokens per evaluation, so costs are minimal for personal/testing use.

## 🔄 Switching Back to Vertex AI

If you want to switch back to Vertex AI:

1. Update your `.env` file:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   LLM_MODEL=gemini-2.0-flash-exp
   ```

2. Set up Google Cloud authentication:
   ```bash
   gcloud auth application-default login
   ```

3. Install additional dependencies:
   ```bash
   pip install google-cloud-aiplatform google-cloud-automl
   ```

## 📝 What Changed

✅ **Simplified dependencies**: Removed heavy Google Cloud packages
✅ **Easier setup**: Just need an API key, no Google Cloud project
✅ **Same functionality**: All features work exactly the same
✅ **Better error handling**: Clearer messages for common issues
✅ **Flexible**: Can switch between Google AI Studio and Vertex AI

## 🎯 Next Steps

1. Test the basic functionality
2. Try the AI-generated scenarios feature
3. Practice with different difficulty levels
4. Export your progress data for analysis

Happy prompting! 🚀
