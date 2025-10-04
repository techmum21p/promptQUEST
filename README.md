# 🎯 Gamified Prompt Engineering Training App

A comprehensive training platform to help your non-tech teammates master prompt engineering for Microsoft 365 Copilot using Google Agent Development Kit (ADK) and Gemini on Vertex AI.

## 🌟 Features

- **Gamification Elements**
  - Score tracking with detailed breakdowns
  - User leaderboard
  - Badge system (Perfect Score, Consistent Performer, Dedicated Learner, Advanced Master)
  - Skill level progression (Beginner → Intermediate → Advanced)

- **Practice Scenarios**
  - Microsoft 365 Copilot-specific scenarios
  - Real-world use cases for Outlook, Word, Excel, PowerPoint, and Teams
  - Three difficulty levels with 3 scenarios each
  - Hints and example prompts for learning

- **AI-Powered Evaluation**
  - Comprehensive scoring across 4 dimensions (Clarity, Specificity, Structure, Task Alignment)
  - Detailed constructive feedback
  - Identification of strengths and improvement areas
  - Powered by Google ADK and Gemini 2.0 Flash

- **Progress Tracking**
  - Persistent user data storage
  - Historical attempt records
  - Performance analytics
  - Learning resources and best practices

## 📋 Prerequisites

- Python 3.9 or higher
- Google Cloud Project with Vertex AI API enabled
- gcloud CLI installed and configured

## 🚀 Installation

### 1. Clone or Create Project Structure

```bash
mkdir prompt-training-app
cd prompt-training-app
```

Create the following file structure:
```
prompt-training-app/
├── prompt_training_app.py    # Main application with ADK agents
├── streamlit_app.py           # Streamlit UI
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create from .env.example)
├── .env.example              # Template for environment variables
└── user_progress.json        # Auto-generated user data (don't create manually)
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Google Cloud Authentication

#### Option A: Using Vertex AI (Recommended for Production)

1. Create a Google Cloud Project at https://console.cloud.google.com
2. Enable the Vertex AI API:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```
3. Authenticate:
   ```bash
   gcloud auth application-default login
   ```
4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
5. Edit `.env` and add your project details:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=TRUE
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

#### Option B: Using Google AI Studio (For Quick Testing)

1. Get an API key from https://aistudio.google.com/apikey
2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env`:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your-api-key-here
   ```

## 🎮 Running the Application

### Local Testing

```bash
# Make sure you're in the project directory and virtual environment is activated
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### First Time Usage

1. Enter a username on the login screen
2. Click "Start Training"
3. Navigate to "Practice Mode" in the sidebar
4. Select a difficulty level
5. Choose or get a random scenario
6. Write your prompt
7. Submit for AI evaluation
8. Review feedback and improve!

## 📚 How It Works

### Architecture

```
┌─────────────────────────────────────────────────┐
│          Streamlit UI (streamlit_app.py)        │
│  - User Interface                                │
│  - Navigation & Session Management              │
│  - Results Display                              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│    Core Logic (prompt_training_app.py)          │
│  - PromptEvaluatorAgent (Google ADK)            │
│  - CopilotScenarioGenerator                     │
│  - UserProgressTracker                          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      Google Vertex AI / Gemini API              │
│  - Gemini 2.0 Flash Model                       │
│  - Prompt Evaluation                            │
│  - Structured Feedback Generation               │
└─────────────────────────────────────────────────┘
```

### Evaluation Criteria

Each prompt is evaluated on 4 dimensions (25 points each):

1. **Clarity (25 points)**: Is the prompt clear and unambiguous?
2. **Specificity (25 points)**: Does it provide enough context and details?
3. **Structure (25 points)**: Is it well-organized with proper formatting?
4. **Task Alignment (25 points)**: Does it align with the given scenario/goal?

**Total Score: 100 points**

### Scoring Tiers
- 🌟 **Excellent**: 85-100 points
- 👍 **Good**: 70-84 points
- 💪 **Needs Practice**: 0-69 points

### Badge System

- **Perfect Score**: Achieve 100/100 on any scenario
- **Consistent Performer**: Score above 80 on 3 attempts
- **Dedicated Learner**: Complete 10 practice attempts
- **Advanced Master**: Complete 5 advanced scenarios with average > 85

### Skill Level Progression

- **Beginner**: Starting level
- **Intermediate**: Average score ≥70 with 3+ attempts
- **Advanced**: Average score ≥85 with 5+ attempts

## 🎯 Practice Scenarios

### Beginner Level
1. Email Summarization in Outlook
2. Document Formatting in Word
3. Meeting Preparation in Teams

### Intermediate Level
1. Data Analysis in Excel
2. Presentation Creation in PowerPoint
3. Cross-Product Workflow

### Advanced Level
1. Strategic Analysis in Business Chat
2. Complex Automation Workflow
3. Enterprise Knowledge Synthesis

## 💾 Data Persistence

User progress is automatically saved to `user_progress.json` in the project directory. This includes:
- User scores and attempts
- Skill level progression
- Badge achievements
- Complete attempt history
- Leaderboard rankings

## 🔧 Customization

### Adding New Scenarios

Edit `prompt_training_app.py` and add scenarios to the `CopilotScenarioGenerator.get_scenarios()` method:

```python
{
    "id": "b4",  # Unique ID
    "title": "Your Scenario Title",
    "description": "Scenario description",
    "goal": "What users should accomplish",
    "context": "Additional context",
    "product": "Microsoft 365 Product",
    "hints": ["Hint 1", "Hint 2"],
    "example_good": "Example of a good prompt"
}
```

### Adjusting Evaluation Criteria

Modify the `instruction` parameter in the `PromptEvaluatorAgent.__init__()` method to change how prompts are evaluated.

### Customizing UI

Edit `streamlit_app.py` to modify colors, layouts, or add new pages. The custom CSS is in the `st.markdown()` section at the top.

## 🚫 Troubleshooting

### "Authentication Error"
- Make sure you've run `gcloud auth application-default login`
- Check that your `.env` file has the correct project ID

### "Module not found"
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### "Model not found"
- Verify Vertex AI API is enabled in your Google Cloud project
- Check that the model name is correct (gemini-2.0-flash)
- Ensure your region supports Gemini models (us-central1 is recommended)

### "JSON Parsing Error"
- This occasionally happens with LLM responses
- The app includes fallback handling
- Try submitting again if this occurs

### Streamlit won't start
- Check if port 8501 is already in use
- Try: `streamlit run streamlit_app.py --server.port 8502`

### Slow responses
- First API call may be slow due to cold start
- Subsequent calls should be faster
- Consider using a more powerful machine type if deploying to cloud

## 📊 Usage Analytics

The app tracks the following metrics per user:
- Total attempts
- Average score across all attempts
- Score breakdown by category
- Skill level progression over time
- Badge achievements
- Complete attempt history with timestamps

## 🎓 Best Practices for Training Sessions

### For Trainers

1. **Start with Basics**
   - Begin with beginner scenarios
   - Demonstrate good vs. poor prompts
   - Explain the evaluation criteria

2. **Hands-On Practice**
   - Let users practice independently
   - Encourage experimentation
   - Review feedback together

3. **Group Learning**
   - Share high-scoring prompts
   - Discuss different approaches
   - Use leaderboard for friendly competition

4. **Progressive Difficulty**
   - Master beginner level first
   - Move to intermediate when comfortable
   - Advanced scenarios for power users

### For Learners

1. **Read Scenarios Carefully**
   - Understand the context
   - Identify the goal
   - Note the product being used

2. **Use the Hints**
   - Check hints before writing
   - Look at example prompts
   - Learn from patterns

3. **Iterate and Improve**
   - Review feedback carefully
   - Try scenarios multiple times
   - Apply learnings to next attempts

4. **Track Progress**
   - Monitor your score trends
   - Set personal goals
   - Celebrate badge achievements

## 🔐 Security Considerations

- **Authentication**: Uses Google Cloud authentication (ADC or API key)
- **Data Privacy**: User data stored locally in `user_progress.json`
- **API Keys**: Never commit `.env` file to version control
- **Credentials**: Keep service account keys secure
- **Network**: Ensure secure connection to Vertex AI endpoints

### For Production Deployment

1. Use service accounts with minimal required permissions
2. Store secrets in Google Secret Manager
3. Enable VPC Service Controls if needed
4. Implement proper access controls
5. Monitor API usage and costs

## 💰 Cost Considerations

### Vertex AI Pricing

- Gemini 2.0 Flash is cost-effective for this use case
- Typical costs: ~$0.10-0.30 per 1000 evaluations
- Monitor usage in Google Cloud Console
- Set up billing alerts

### Free Tier Options

- Google AI Studio offers free API access for testing
- Vertex AI has a free tier with monthly credits
- Perfect for initial testing and small teams

## 🚀 Deployment to Google Cloud Run (Future)

While this README focuses on local testing, here's what you'll need for cloud deployment:

### Prerequisites for Cloud Run
- Docker installed
- Cloud Run API enabled
- Container Registry or Artifact Registry access

### Files Needed (To Be Created)
- `Dockerfile`
- `cloudbuild.yaml` or deployment script
- Updated `.env` handling for Cloud Run secrets

### Deployment Steps (High-Level)
1. Containerize the application
2. Build and push to Container Registry
3. Deploy to Cloud Run
4. Configure environment variables as secrets
5. Set up authentication and IAM
6. Configure custom domain (optional)

**Note**: Cloud deployment instructions will be provided separately when you're ready to deploy.

## 📈 Extending the Application

### Potential Enhancements

1. **Multi-Language Support**
   - Add internationalization
   - Support for non-English prompts

2. **Advanced Analytics**
   - Team performance dashboards
   - Trend analysis over time
   - Common mistake patterns

3. **Integration Features**
   - Export progress reports
   - Share prompts with team
   - Import custom scenarios

4. **Adaptive Learning**
   - Personalized scenario recommendations
   - Dynamic difficulty adjustment
   - AI-generated practice scenarios

5. **Social Features**
   - Team challenges
   - Prompt sharing and voting
   - Mentor-mentee connections

6. **Admin Dashboard**
   - User management
   - Custom scenario creation UI
   - Performance analytics

## 🧪 Testing

### Manual Testing Checklist

- [ ] User can log in
- [ ] Dashboard displays correct stats
- [ ] Can select and load scenarios
- [ ] Prompt submission works
- [ ] Evaluation returns valid scores
- [ ] Feedback is displayed properly
- [ ] Progress is saved correctly
- [ ] Leaderboard updates
- [ ] Badges are awarded correctly
- [ ] Navigation works smoothly

### Test User Flow

1. Create test user "test_user_1"
2. Complete 1 beginner scenario (aim for 60+ score)
3. Complete 1 beginner scenario (aim for 85+ score)
4. Verify skill level progression
5. Complete 3 more scenarios
6. Check badge awards
7. Verify leaderboard placement

## 🤝 Contributing

If you want to extend this application:

1. Create feature branch
2. Add new scenarios or features
3. Test thoroughly
4. Document changes
5. Update README if needed

## 📝 License

This project is for internal training purposes. Modify as needed for your organization.

## 🆘 Support

### Common Questions

**Q: Can I use this without Google Cloud?**
A: Yes! Use Google AI Studio with a free API key for testing.

**Q: How many users can use this simultaneously?**
A: Locally, one user at a time. For multiple users, deploy to Cloud Run with session management.

**Q: Can I customize the scoring criteria?**
A: Yes! Edit the `PromptEvaluatorAgent` instruction in `prompt_training_app.py`.

**Q: How do I reset a user's progress?**
A: Edit or delete their entry in `user_progress.json`.

**Q: Can I add my own scenarios?**
A: Absolutely! Follow the "Adding New Scenarios" section above.

**Q: What if the AI evaluation seems wrong?**
A: LLMs can be subjective. You can adjust the evaluation prompt or try again. Consider averaging multiple attempts.

### Getting Help

- Check Google ADK documentation: https://google.github.io/adk-docs/
- Review Vertex AI docs: https://cloud.google.com/vertex-ai/docs
- Streamlit documentation: https://docs.streamlit.io
- Google Cloud support for billing/API issues

## 📞 Contact

For questions about this training app or prompt engineering best practices, reach out to your AI Engineering team.

## 🎉 Acknowledgments

- **Google ADK**: For the excellent agent development framework
- **Streamlit**: For the intuitive UI framework
- **Microsoft 365 Copilot**: For the inspiration and use cases
- **Your Team**: For being eager to learn and improve!

---

## 🏁 Quick Start Summary

```bash
# 1. Setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your credentials
gcloud auth application-default login

# 3. Run
streamlit run streamlit_app.py

# 4. Train
# Open browser, create user, start practicing!
```

**Happy Learning! 🚀**

---

*Last Updated: 2025*
*Version: 1.0.0*