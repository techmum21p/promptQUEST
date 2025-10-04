"""
Streamlit UI for Gamified Prompt Engineering Training App
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import from main app
from prompt_training_app import (
    evaluate_user_prompt_async,
    get_scenarios_by_level,
    get_random_scenario_by_level,
    get_ai_scenario_by_level,
    get_mixed_scenario_by_level,
    get_scenario_statistics,
    UserProgressTracker,
    CopilotScenarioGenerator
)

# Page configuration
st.set_page_config(
    page_title="Prompt Engineering Training",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078D4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .scenario-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #0078D4;
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: #FFD700;
        color: #000;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: bold;
    }
    .feedback-excellent {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
    }
    .feedback-good {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
    }
    .feedback-needs-work {
        background: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
    }
    .leaderboard-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = UserProgressTracker()

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'current_scenario' not in st.session_state:
    st.session_state.current_scenario = None

if 'show_results' not in st.session_state:
    st.session_state.show_results = False

if 'scenario_generation_mode' not in st.session_state:
    st.session_state.scenario_generation_mode = "preset"  # preset, ai, or mixed

if 'ai_probability' not in st.session_state:
    st.session_state.ai_probability = 0.3


def render_login():
    """Render login/user selection"""
    st.markdown("<div class='main-header'>🎯 Prompt Engineering Training Hub</div>", unsafe_allow_html=True)
    st.markdown("### Welcome to PromptQuest! Let's improve your prompt engineering skills for Copilot")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username = st.text_input("Enter your username:", key="username_input")
        
        if st.button("Start Training", type="primary", use_container_width=True):
            if username:
                st.session_state.tracker.add_user(username)
                st.session_state.current_user = username
                st.rerun()
            else:
                st.error("Please enter a username")


def render_dashboard():
    """Render main dashboard"""
    user = st.session_state.current_user
    stats = st.session_state.tracker.get_user_stats(user)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div class='main-header'>🎯 Prompt Engineering Training</div>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", type="secondary"):
            st.session_state.current_user = None
            st.session_state.current_scenario = None
            st.session_state.show_results = False
            st.rerun()
    
    st.markdown(f"### Welcome back, **{user}**! 👋")
    
    # User stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    avg_score = stats["total_score"] / stats["attempts"] if stats["attempts"] > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class='score-card'>
            <h2>{stats['attempts']}</h2>
            <p>Total Attempts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='score-card'>
            <h2>{avg_score:.1f}</h2>
            <p>Average Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='score-card'>
            <h2>{stats['skill_level'].title()}</h2>
            <p>Skill Level</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='score-card'>
            <h2>{len(stats['badges'])}</h2>
            <p>Badges Earned</p>
        </div>
        """, unsafe_allow_html=True)
    
        if stats['badges']:
            st.markdown("### 🏆 Your Badges")
            badge_html = " ".join([f"<span class='badge'>{badge}</span>" for badge in stats['badges']])
            st.markdown(badge_html, unsafe_allow_html=True)
        
        st.markdown("---")


def render_data_export():
    """Render data export section"""
    st.markdown("## 📊 Data Export & Analytics")
    
    # Get export summary
    summary = st.session_state.tracker.get_export_summary()
    
    # Display summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", summary["total_users"])
    with col2:
        st.metric("Active Users", summary["active_users"])
    with col3:
        st.metric("Total Attempts", summary["total_attempts"])
    with col4:
        st.metric("Overall Avg Score", f"{summary['avg_score_all_users']:.1f}")
    
    st.markdown("---")
    
    # Export options
    st.markdown("### 📥 Export Data")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        export_filename = st.text_input(
            "Custom filename (optional):",
            placeholder="e.g., my_export.csv",
            help="Leave empty for auto-generated timestamp filename"
        )
        
        if st.button("📊 Export to CSV", type="primary", use_container_width=True):
            try:
                filename = st.session_state.tracker.export_to_csv(
                    export_filename if export_filename.strip() else None
                )
                if filename:
                    st.success(f"✅ Data exported successfully to: `{filename}`")
                    st.info("💡 You can find this file in your project directory and open it with Excel, Google Sheets, or any data analysis tool.")
                    
                    # Show sample of exported data
                    try:
                        import pandas as pd
                        df = pd.read_csv(filename)
                        st.markdown("### 👀 Preview of Exported Data")
                        st.dataframe(df.head(10), use_container_width=True)
                        
                        # Quick stats from the exported data
                        if len(df) > 0:
                            st.markdown("### 📈 Quick Analytics")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Records Exported", len(df))
                            with col2:
                                avg_score = df[df['total_score'] > 0]['total_score'].mean()
                                st.metric("Average Score", f"{avg_score:.1f}" if not pd.isna(avg_score) else "N/A")
                            with col3:
                                unique_scenarios = df[df['scenario_id'] != '']['scenario_id'].nunique()
                                st.metric("Unique Scenarios", unique_scenarios)
                    except Exception as e:
                        st.warning(f"Could not preview data: {str(e)}")
                else:
                    st.warning("No data to export - no users have made attempts yet.")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
                st.info("Make sure pandas is installed: `pip install pandas`")
    
    with col2:
        st.markdown("#### 🔄 Quick Export")
        if st.button("📄 Export Now with Timestamp", use_container_width=True):
            try:
                filename = st.session_state.tracker.export_to_csv()
                if filename:
                    st.success(f"✅ Exported to: `{filename}`")
                else:
                    st.warning("No data to export")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    # What's included section - full width for better readability
    st.markdown("---")
    st.markdown("### 📋 What's Included in Export")
    
    # Use containers for better layout
    info_container = st.container()
    with info_container:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **👤 User Information:**
            - Username and skill level  
            - Total attempts and cumulative score
            - Average score and badges earned
            """)
        
        with col2:
            st.markdown("""
            **📊 Attempt Details:**
            - Timestamp of each attempt
            - Scenario ID attempted  
            - User's original prompt text
            - Score breakdown (clarity, specificity, structure, alignment)
            """)
        
        with col3:
            st.markdown("""
            **🎯 Learning Insights:**
            - AI-identified strengths
            - Areas for improvement suggestions
            - Detailed feedback summary
            - Compatible with Excel, Google Sheets, Python, R
            """)
    
    st.markdown("---")
    
    # Export usage tips section
    if st.button("📝 Export Usage Tips", use_container_width=True):
        st.markdown("""
        ### 💡 Data Analysis Ideas
        
        **Excel/Google Sheets:**
        - Create pivot tables to analyze performance by scenario
        - Generate charts showing improvement over time
        - Filter by skill level or score ranges
        
        **Python Analysis:**
        ```python
        import pandas as pd
        df = pd.read_csv('your_export.csv')
        
        # User performance trends
        df.groupby('username')['total_score'].mean()
        
        # Scenario difficulty analysis
        df.groupby('scenario_id')['total_score'].agg(['mean', 'count'])
        
        # Learning progress over time
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.plot(x='timestamp', y='total_score')
        ```
        """)
    
    st.markdown("---")
    
    # Auto-backup status
    if summary["total_users"] > 0:
        st.markdown("### 🔄 Auto-Backup Status")
        next_backup = ((summary["active_users"] // 5) + 1) * 5
        st.info(f"📅 Next automatic backup will be created at {next_backup} active users (currently: {summary['active_users']})")


def render_admin_panel():
    """Render admin panel for data management"""
    st.markdown("## ⚙️ Admin Panel")
    
    st.warning("🔧 Administrative functions - use with caution!")
    
    # Data management
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗃️ Data Management")
        
        if st.button("🔄 Refresh Data", help="Reload data from JSON file"):
            st.session_state.tracker = UserProgressTracker()
            st.success("Data refreshed successfully!")
            st.rerun()
        
        if st.button("📋 View Raw JSON", help="Display raw JSON data structure"):
            st.json(st.session_state.tracker.data)
    
    with col2:
        st.markdown("### 📁 File Information")
        
        try:
            import os
            json_file = "user_progress.json"
            if os.path.exists(json_file):
                file_size = os.path.getsize(json_file)
                mod_time = os.path.getmtime(json_file)
                
                st.metric("File Size", f"{file_size} bytes")
                st.metric("Last Modified", datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S"))
            else:
                st.warning("JSON file not found")
        except Exception as e:
            st.error(f"Could not read file info: {str(e)}")
    
    # Backup management
    st.markdown("### 💾 Backup Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆘 Create Emergency Backup", type="secondary", use_container_width=True):
            try:
                filename = st.session_state.tracker.export_to_csv(f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                if filename:
                    st.success(f"Emergency backup created: {filename}")
                else:
                    st.warning("No data to backup")
            except Exception as e:
                st.error(f"Backup failed: {str(e)}")
    
    with col2:
        st.markdown("**Recommended Actions:**")
        st.markdown("- Export data regularly for analysis")
        st.markdown("- Keep backups before major updates")
        st.markdown("- Monitor file size as users grow")


def render_practice_mode():
    """Render practice mode"""
    user = st.session_state.current_user
    stats = st.session_state.tracker.get_user_stats(user)
    
    st.markdown("## 📝 Practice Mode")
    
    # Scenario generation mode selection
    st.markdown("### 🎲 Scenario Generation")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        generation_mode = st.selectbox(
            "Choose scenario source:",
            ["preset", "ai", "mixed"],
            format_func=lambda x: {
                "preset": "📚 Preset Scenarios (Curated by experts)",
                "ai": "🤖 AI-Generated Scenarios (Fresh & dynamic)",
                "mixed": "🎲 Mixed Mode (Blend of preset & AI)"
            }[x],
            index=["preset", "ai", "mixed"].index(st.session_state.scenario_generation_mode),
            help="Preset scenarios are curated examples. AI-generated scenarios are created dynamically using the preset scenarios as examples for few-shot prompting."
        )
        st.session_state.scenario_generation_mode = generation_mode
    
    with col2:
        if generation_mode == "mixed":
            ai_prob = st.slider(
                "AI Generation Probability:",
                min_value=0.1,
                max_value=0.9,
                value=st.session_state.ai_probability,
                step=0.1,
                help="Probability of getting an AI-generated scenario vs preset"
            )
            st.session_state.ai_probability = ai_prob
    
    # Display scenario statistics
    if generation_mode in ["preset", "mixed"]:
        scenario_stats = get_scenario_statistics()
        st.info(f"📊 Available preset scenarios: {scenario_stats['total_preset']} total "
                f"({scenario_stats['beginner_count']} beginner, "
                f"{scenario_stats['intermediate_count']} intermediate, "
                f"{scenario_stats['advanced_count']} advanced)")
    
    # Skill level and scenario selection
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_level = st.selectbox(
            "Choose difficulty level:",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(stats['skill_level'])
        )
    
    with col2:
        scenario_button_text = {
            "preset": "Get Random Preset Scenario",
            "ai": "🤖 Generate AI Scenario",
            "mixed": "🎲 Get Random Scenario"
        }[generation_mode]
        
        if st.button(scenario_button_text, type="primary", use_container_width=True):
            with st.spinner("🤖 Generating scenario..." if generation_mode != "preset" else "Loading scenario..."):
                try:
                    if generation_mode == "preset":
                        st.session_state.current_scenario = get_random_scenario_by_level(selected_level)
                    elif generation_mode == "ai":
                        st.session_state.current_scenario = asyncio.run(
                            get_ai_scenario_by_level(selected_level)
                        )
                    else:  # mixed
                        st.session_state.current_scenario = asyncio.run(
                            get_mixed_scenario_by_level(selected_level, st.session_state.ai_probability)
                        )
                    
                    st.session_state.show_results = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating scenario: {str(e)}")
                    st.info("Falling back to preset scenario...")
                    st.session_state.current_scenario = get_random_scenario_by_level(selected_level)
                    st.session_state.show_results = False
                    st.rerun()
    
    # Preset scenario selection (only show for preset mode)
    if generation_mode == "preset":
        scenarios = get_scenarios_by_level(selected_level)
        scenario_options = {f"{s['id']}: {s['title']}": s for s in scenarios}
        
        if not st.session_state.current_scenario:
            selected = st.selectbox(
                "Or select a specific preset scenario:",
                list(scenario_options.keys())
            )
            
            if st.button("Load This Scenario", use_container_width=True):
                st.session_state.current_scenario = scenario_options[selected]
                st.session_state.show_results = False
                st.rerun()
    
    # Display current scenario
    if st.session_state.current_scenario:
        scenario = st.session_state.current_scenario
        
        # Show scenario source indicator
        scenario_source = "🤖 AI-Generated" if scenario.get('id', '').endswith('99') or generation_mode == "ai" else "📚 Preset"
        
        st.markdown(f"""
        <div class='scenario-card'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                <h3>📋 {scenario['title']}</h3>
                <span style='background: #e1f5fe; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem;'>{scenario_source}</span>
            </div>
            <p><strong>Product:</strong> {scenario['product']}</p>
            <p><strong>Scenario:</strong> {scenario['description']}</p>
            <p><strong>Goal:</strong> {scenario['goal']}</p>
            <p><strong>Context:</strong> {scenario['context']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Hints expander
        with st.expander("💡 Need hints?"):
            for i, hint in enumerate(scenario['hints'], 1):
                st.write(f"{i}. {hint}")
            
            if st.checkbox("Show example of a good prompt"):
                st.success(f"**Example:** {scenario['example_good']}")
        
        # Prompt input
        st.markdown("### ✍️ Write Your Prompt")
        user_prompt = st.text_area(
            "Enter your prompt here:",
            height=150,
            placeholder="Write your prompt for the scenario above...",
            key="user_prompt_input"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit_button = st.button("Submit for Evaluation", type="primary", use_container_width=True)
        with col2:
            new_scenario_text = {
                "preset": "Try Different Preset Scenario",
                "ai": "🤖 Generate New AI Scenario",
                "mixed": "🎲 Get Another Random Scenario"
            }[generation_mode]
            
            if st.button(new_scenario_text, use_container_width=True):
                st.session_state.current_scenario = None
                st.session_state.show_results = False
                st.rerun()
        
        # Evaluate prompt
        if submit_button:
            if user_prompt.strip():
                with st.spinner("🤖 AI is evaluating your prompt..."):
                    try:
                        # Run async evaluation
                        evaluation = asyncio.run(
                            evaluate_user_prompt_async(user_prompt, scenario)
                        )
                        
                        # Record attempt
                        st.session_state.tracker.record_attempt(
                            user,
                            scenario['id'],
                            evaluation['total_score'],
                            evaluation,
                            user_prompt
                        )
                        
                        # Store results in session state
                        st.session_state.evaluation_results = evaluation
                        st.session_state.show_results = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during evaluation: {str(e)}")
                        st.info("Please make sure your Vertex AI credentials are properly configured in the .env file")
            else:
                st.warning("Please write a prompt before submitting")
        
        # Display results
        if st.session_state.show_results and 'evaluation_results' in st.session_state:
            evaluation = st.session_state.evaluation_results
            
            st.markdown("---")
            st.markdown("## 📊 Evaluation Results")
            
            # Score display
            score = evaluation['total_score']
            if score >= 85:
                feedback_class = "feedback-excellent"
                emoji = "🌟"
                message = "Excellent!"
            elif score >= 70:
                feedback_class = "feedback-good"
                emoji = "👍"
                message = "Good job!"
            else:
                feedback_class = "feedback-needs-work"
                emoji = "💪"
                message = "Keep practicing!"
            
            st.markdown(f"""
            <div class='{feedback_class}'>
                <h2>{emoji} {message} Your Score: {score}/100</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed scores
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Clarity", f"{evaluation['clarity_score']}/25")
            with col2:
                st.metric("Specificity", f"{evaluation['specificity_score']}/25")
            with col3:
                st.metric("Structure", f"{evaluation['structure_score']}/25")
            with col4:
                st.metric("Task Alignment", f"{evaluation['task_alignment_score']}/25")
            
            # Detailed feedback
            st.markdown("### 💬 Detailed Feedback")
            st.info(evaluation['feedback'])
            
            # Strengths
            if evaluation.get('strengths'):
                st.markdown("### ✅ Strengths")
                for strength in evaluation['strengths']:
                    st.success(f"✓ {strength}")
            
            # Areas for improvement
            if evaluation.get('improvements'):
                st.markdown("### 🔧 Areas for Improvement")
                for improvement in evaluation['improvements']:
                    st.warning(f"→ {improvement}")
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Try This Scenario Again", use_container_width=True):
                    st.session_state.show_results = False
                    st.rerun()
            with col2:
                next_scenario_text = {
                    "preset": "Next Preset Scenario",
                    "ai": "🤖 Generate New AI Scenario",
                    "mixed": "🎲 Next Random Scenario"
                }[generation_mode]
                
                if st.button(next_scenario_text, type="primary", use_container_width=True):
                    st.session_state.current_scenario = None
                    st.session_state.show_results = False
                    st.rerun()


def render_leaderboard():
    """Render leaderboard"""
    st.markdown("## 🏆 Leaderboard")
    st.markdown("### Top Performers")
    
    leaderboard = st.session_state.tracker.get_leaderboard(top_n=20)
    
    if leaderboard:
        # Create leaderboard display
        for i, entry in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
            with col1:
                st.markdown(f"### {medal}")
            with col2:
                st.markdown(f"**{entry['username']}**")
            with col3:
                st.markdown(f"Score: **{entry['avg_score']:.1f}**")
            with col4:
                st.markdown(f"Level: **{entry['skill_level'].title()}**")
            with col5:
                st.markdown(f"🏅 **{entry['badges']}** badges")
            
            st.markdown("---")
    else:
        st.info("No entries yet. Be the first to complete a challenge!")


def render_progress_history():
    """Render user progress history"""
    user = st.session_state.current_user
    stats = st.session_state.tracker.get_user_stats(user)
    
    st.markdown("## 📈 Your Progress History")
    
    if stats['history']:
        st.markdown(f"### Total Attempts: {len(stats['history'])}")
        
        # Show recent attempts
        for i, attempt in enumerate(reversed(stats['history'][-10:]), 1):
            with st.expander(f"Attempt {len(stats['history']) - i + 1}: Score {attempt['score']}/100 - {attempt['scenario_id']} ({attempt['timestamp'][:10]})"):
                st.write(f"**Score Breakdown:**")
                eval_data = attempt['evaluation']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Clarity", f"{eval_data.get('clarity_score', 0)}/25")
                with col2:
                    st.metric("Specificity", f"{eval_data.get('specificity_score', 0)}/25")
                with col3:
                    st.metric("Structure", f"{eval_data.get('structure_score', 0)}/25")
                with col4:
                    st.metric("Alignment", f"{eval_data.get('task_alignment_score', 0)}/25")
                
                # Show user's original prompt
                user_prompt = attempt.get('user_prompt', '')
                if user_prompt:
                    st.write("**Your Original Prompt:**")
                    st.code(user_prompt, language="text")
                else:
                    st.write("**Your Original Prompt:** *(Not recorded)*")
                
                # Show strengths and improvements
                col1, col2 = st.columns(2)
                
                with col1:
                    strengths = eval_data.get('strengths', [])
                    if strengths:
                        st.write("**✅ Strengths:**")
                        for strength in strengths:
                            st.success(f"✓ {strength}")
                
                with col2:
                    improvements = eval_data.get('improvements', [])
                    if improvements:
                        st.write("**🔧 Areas for Improvement:**")
                        for improvement in improvements:
                            st.warning(f"→ {improvement}")
                
                st.write("**💬 Detailed Feedback:**")
                st.info(eval_data.get('feedback', 'No feedback available'))
    else:
        st.info("No attempts yet. Start practicing to see your progress!")


def render_learning_resources():
    """Render learning resources"""
    st.markdown("## 📚 Learning Resources")
    
    st.markdown("""
    ### 🎯 AI-Powered Scenario Generation
    
    This app now features **AI-Generated Scenarios** that provide unlimited practice opportunities:
    
    #### 🤖 How It Works
    - **Few-Shot Prompting**: The AI uses our curated preset scenarios as examples
    - **Dynamic Generation**: Creates fresh scenarios that match the difficulty level
    - **Quality Consistency**: Maintains the same structure and educational value as preset scenarios
    
    #### 🎲 Scenario Modes
    1. **📚 Preset Scenarios**: Hand-crafted by experts, tested and refined
    2. **🤖 AI-Generated**: Fresh scenarios created on-demand using advanced AI
    3. **🎲 Mixed Mode**: Randomly combines both types for variety
    
    #### 💡 Benefits of AI Generation
    - **Unlimited Practice**: Never run out of scenarios to practice with
    - **Adaptive Learning**: Each scenario is unique while maintaining difficulty standards
    - **Diverse Challenges**: AI creates scenarios covering various Microsoft 365 use cases
    - **Real-World Relevance**: Generated scenarios reflect current workplace challenges
    
    ---
    
    ### Prompt Engineering Best Practices for Microsoft 365 Copilot
    
    #### 🎯 Core Principles
    
    1. **Be Specific and Clear**
       - Use concrete language
       - Define exactly what you want
       - Avoid ambiguous terms
    
    2. **Provide Context**
       - Mention relevant documents, time periods, or data sources
       - Specify your role or perspective
       - Include constraints or requirements
    
    3. **Structure Your Prompt**
       - Break complex requests into steps
       - Use numbering or bullet points
       - Organize information logically
    
    4. **Iterate and Refine**
       - Start broad, then narrow down
       - Review and adjust based on results
       - Learn from feedback
    
    #### 💼 Product-Specific Tips
    
    **Outlook Copilot:**
    - Specify time ranges for email searches
    - Mention specific senders or subjects
    - Request specific output formats (summary, bullet points, etc.)
    
    **Word Copilot:**
    - Describe the tone and style you want
    - Specify document structure (headings, sections)
    - Mention formatting requirements
    
    **Excel Copilot:**
    - Be clear about data ranges
    - Specify analysis type (trends, comparisons, etc.)
    - Request specific visualization types
    
    **PowerPoint Copilot:**
    - Define your audience
    - Specify number of slides and structure
    - Mention design preferences or templates
    
    **Teams Copilot:**
    - Reference specific channels or time periods
    - Request summaries of discussions or decisions
    - Specify action items or follow-ups needed
    
    #### 🔗 Additional Resources
    - [Microsoft Copilot Documentation](https://support.microsoft.com/copilot)
    - [Prompt Engineering Guide](https://www.promptingguide.ai/)
    - [Microsoft 365 Copilot Best Practices](https://adoption.microsoft.com/copilot/)
    - [Best Microsoft Copilot Prompts--And How to Write Them](https://www.hbs.net/blog/copilot-prompt-help)
    """)
    
    # Add example of how AI scenarios are generated
    with st.expander("🔍 Example: How AI Scenarios Are Generated"):
        st.markdown("""
        **Input to AI:**
        - Difficulty level (e.g., "intermediate")
        - 2-3 preset scenarios as examples (few-shot prompting)
        - Requirements for Microsoft 365 Copilot context
        
        **AI Output:**
        A new scenario with the same structure:
        ```json
        {
            "id": "i4",
            "title": "Customer Data Analysis Dashboard",
            "description": "You need to create an executive dashboard from customer survey data.",
            "goal": "Generate insights and visualizations from customer feedback",
            "context": "Quarterly customer satisfaction survey with 500+ responses",
            "product": "Excel Copilot",
            "hints": ["Specify chart types", "Include trend analysis", "Request key metrics"],
            "example_good": "Create an executive dashboard from Q3 customer survey data..."
        }
        ```
        
        **Quality Assurance:**
        - Same JSON structure as preset scenarios
        - Appropriate difficulty level
        - Realistic Microsoft 365 use case
        - Clear, actionable prompts
        """)
        
        if st.button("🎯 Try AI Generation Now!", type="primary"):
            st.info("👆 Go to **Practice Mode** and select **🤖 AI-Generated Scenarios** to experience this feature!")
    


# Main app logic
def main():
    """Main application logic"""
    
    # If no user logged in, show login
    if not st.session_state.current_user:
        render_login()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        page = st.radio(
            "Go to:",
            ["Dashboard", "Practice Mode", "Leaderboard", "Progress History", "Data Export", "Learning Resources", "Admin Panel"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats in sidebar
        stats = st.session_state.tracker.get_user_stats(st.session_state.current_user)
        st.markdown("### 📊 Quick Stats")
        st.metric("Attempts", stats['attempts'])
        avg_score = stats["total_score"] / stats["attempts"] if stats["attempts"] > 0 else 0
        st.metric("Avg Score", f"{avg_score:.1f}")
        st.metric("Skill Level", stats['skill_level'].title())
        
        st.markdown("---")
        st.markdown("### ℹ️ About Prompt Quest")
        st.info("Gamified Prompt Engineering Training for Microsoft 365 Copilot. Powered by Google ADK and Vertex AI.")
    
    # Render dashboard for all pages
    render_dashboard()
    
    # Render selected page
    if page == "Dashboard":
        st.markdown("### 🚀 Ready to practice?")
        st.markdown("Use the sidebar to navigate to **Practice Mode** and start improving your prompt engineering skills!")
        
        # Show quick start guide
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            #### 1️⃣ Choose Level
            Select your skill level: Beginner, Intermediate, or Advanced
            """)
        with col2:
            st.markdown("""
            #### 2️⃣ Write Prompt
            Craft a prompt for the given scenario
            """)
        with col3:
            st.markdown("""
            #### 3️⃣ Get Feedback
            Receive AI-powered evaluation and improve
            """)
    
    elif page == "Practice Mode":
        render_practice_mode()
    
    elif page == "Leaderboard":
        render_leaderboard()
    
    elif page == "Progress History":
        render_progress_history()
    
    elif page == "Data Export":
        render_data_export()
    
    elif page == "Learning Resources":
        render_learning_resources()
    
    elif page == "Admin Panel":
        render_admin_panel()


if __name__ == "__main__":
    main()