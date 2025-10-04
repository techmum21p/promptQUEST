"""
Streamlit UI for Prompt Training App with PostgreSQL Database Integration
Enhanced with comprehensive authentication and onboarding flow
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import our database-enabled application
from prompt_training_app_db import (
    PromptEvaluatorAgent, CopilotScenarioGenerator, UserProgressTrackerDB,
    evaluate_user_prompt_async, get_scenarios_by_level, get_random_scenario_by_level,
    get_ai_scenario_by_level, get_scenario_statistics,
    init_app, cleanup_app
)

# Import batch management and authentication
from batch_manager import BatchManager
from auth_manager import AuthenticationManager, require_authentication, get_current_user, is_logged_in

# Page configuration
st.set_page_config(
    page_title="Prompt Training (Database Edition)",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS from original streamlit_app.py
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
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False


if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'current_scenario' not in st.session_state:
    st.session_state.current_scenario = None

if 'show_results' not in st.session_state:
    st.session_state.show_results = False

if 'scenario_generation_mode' not in st.session_state:
    st.session_state.scenario_generation_mode = "preset"

if 'user_progress_session' not in st.session_state:
    st.session_state.user_progress_session = {
        'attempts': 0,
        'total_score': 0,
        'history': [],
        'avg_score': 0,
        'current_skill_level': 'beginner',
        'badges': [],
        'timestamp': datetime.now().isoformat()
    }

if 'batch_manager' not in st.session_state:
    st.session_state.batch_manager = None

if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False


class HybridProgressTracker:
    """Hybrid tracker that uses session state for recent attempts and DB for persistence"""
    
    def __init__(self):
        self.db_tracker = None
        
    async def get_user_stats(self, ldap_id: str) -> Dict:
        """Get user stats from session first, then fallback to DB if available"""
        # Get stats from session
        session_stats = st.session_state.user_progress_session
        
        # Try to get from DB if initialized and available
        if self.db_tracker and st.session_state.get('db_initialized', False):
            try:
                db_stats = await self.db_tracker.get_user_stats(ldap_id)
                if db_stats and db_stats.get('total_attempts', 0) > 0:
                    return db_stats
            except Exception as e:
                print(f"Could not fetch DB stats: {e}")
                # Fall back to session stats silently
        
        # Return session stats as fallback
        return {
            'attempts': session_stats['attempts'],
            'avg_score': session_stats['avg_score'],
            'total_score': session_stats['total_score'],
            'current_skill_level': session_stats['current_skill_level'],
            'badges': session_stats['badges'],
            'history': session_stats['history']
        }
    
    async def record_attempt(self, ldap_id: str, scenario_id: str, score: int, evaluation: Dict, user_prompt: str = ""):
        """Record attempt in session, and to DB if user has 5+ attempts"""
        session_stats = st.session_state.user_progress_session
        
        # Update session stats
        session_stats['attempts'] += 1
        session_stats['total_score'] += score
        session_stats['avg_score'] = session_stats['total_score'] / session_stats['attempts']
        
        # Store in session history
        attempt_record = {
            'scenario_id': scenario_id,
            'score': score,
            'timestamp': datetime.now().isoformat(),
            'evaluation': evaluation,
            'user_prompt': user_prompt
        }
        session_stats['history'].append(attempt_record)
        
        # Update skill level based on avg score (original logic copied from prompt_training_app.py)
        avg_score = session_stats['avg_score']
        if avg_score >= 85 and session_stats['attempts'] >= 5:
            session_stats['current_skill_level'] = 'advanced'
        elif avg_score >= 70 and session_stats['attempts'] >= 3:
            session_stats['current_skill_level'] = 'intermediate'
        else:
            session_stats['current_skill_level'] = 'beginner'
        
        # Determine badges (original logic copied from prompt_training_app.py)
        badges = session_stats.get('badges', [])
        
        # Perfect Score badge
        if any(h['score'] == 100 for h in session_stats['history']) and "Perfect Score" not in badges:
            badges.append("Perfect Score")
        
        # Consistent Performer badge (3 attempts with score > 80)
        high_scores = [h for h in session_stats['history'] if h['score'] > 80]
        if len(high_scores) >= 3 and "Consistent Performer" not in badges:
            badges.append("Consistent Performer")
        
        # Dedicated Learner badge (10 attempts)
        if session_stats['attempts'] >= 10 and "Dedicated Learner" not in badges:
            badges.append("Dedicated Learner")
        
        # Advanced Master badge (5 advanced scenarios with avg > 85)
        advanced_attempts = [h for h in session_stats['history'] if h['scenario_id'].startswith("a")]
        if len(advanced_attempts) >= 5:
            avg_advanced = sum(h['score'] for h in advanced_attempts) / len(advanced_attempts)
            if avg_advanced > 85 and "Advanced Master" not in badges:
                badges.append("Advanced Master")
        
        session_stats['badges'] = badges
        
        # Copy back to session state
        st.session_state.user_progress_session = session_stats
        
        # Save to DB if user has 5+ attempts or if it's a milestone attempt
        if (session_stats['attempts'] >= 5 and 
            self.db_tracker and 
            st.session_state.get('db_initialized', False)):
            try:
                await self.db_tracker.record_attempt(
                    ldap_id, scenario_id, score, evaluation, user_prompt
                )
            except Exception as e:
                error_msg = str(e)
                if "Event loop is closed" in error_msg or "Streamlit lifecycle" in error_msg:
                    print("Database temporarily unavailable (Streamlit rerun)")
                    # Don't persist this error, just continue
                else:
                    print(f"Database save error: {e}")
                    # Continue execution without database persistence

    async def get_leaderboard(self, top_n: int = 20, group: str = None):
        """Get leaderboard - try DB first, fallback to session data"""
        if self.db_tracker and st.session_state.get('db_initialized', False):
            try:
                return await self.db_tracker.get_leaderboard(top_n=top_n, group=group)
            except Exception as e:
                print(f"Leaderboard DB error: {e}")
                # Don't show warning to user, silently fall back
                
        # Fallback: return empty list for now
        return []
    
    async def get_multi_group_leaderboard(self, limit_per_group: int = 20):
        """Get leaderboard organized by groups plus overall"""
        if self.db_tracker and st.session_state.get('db_initialized', False):
            try:
                return await self.db_tracker.get_multi_group_leaderboard(limit_per_group)
            except Exception as e:
                print(f"Multi-group leaderboard DB error: {e}")
                # Don't show warning to user, silently fall back
        
        # Fallback: return empty dict for now
        return {}


async def initialize_database():
    """Initialize database if not already done - Streamlit-friendly version"""
    if not st.session_state.get('db_initialized', False):
        try:
            # Initialize database services only once
            await init_app()
            
            # Initialize batch manager
            st.session_state.batch_manager = BatchManager()
            
            # Mark as initialized
            st.session_state.db_initialized = True
            st.session_state.db_initialization_attempt = True
            print("✅ Database initialized successfully")
            return True
        except Exception as e:
            error_msg = f"Failed to initialize database: {e}"
            print(f"❌ {error_msg}")
            
            # Store the error for user display
            st.session_state.db_error = str(e)
            st.session_state.db_initialization_attempt = True
            
            # Try to continue without database for limited functionality
            print("⚠️ Running in limited mode without database features")
            st.session_state.db_initialized = False
            return False
    return True


async def run_authentication_flow():
    """Run the enhanced authentication flow"""
    # Only try to initialize database once per session
    if not st.session_state.get('db_initialization_attempt', False):
        db_available = await initialize_database()
        
        # Show database status if there's an error
        if not db_available and st.session_state.get('db_error'):
            st.error(f"⚠️ Database connection issue: {st.session_state.db_error}")
            st.info("Running in limited mode with session-based functionality.")
            st.info("Features like admin panel CSV export may not be available.")
    
    auth_manager = AuthenticationManager()
    
    # If user clicked to proceed to main app
    if st.session_state.get('proceed_app'):
        st.session_state.proceed_app = False
        await run_main_application()
        return
    
    if st.session_state.get('view_progress_app'):
        st.session_state.view_progress_app = False
        await run_progress_view()
        return
    
    if st.session_state.get('view_leaderboard_app'):
        st.session_state.view_leaderboard_app = False
        await run_leaderboard_view()
        return
    
    # Run the authentication flow
    await auth_manager.run_auth_flow()


async def run_progress_view():
    """Run progress viewing application"""
    require_authentication()
    
    await initialize_database()
    user = get_current_user()
    tracker = HybridProgressTracker()
    if st.session_state.db_initialized:
        tracker.db_tracker = UserProgressTrackerDB()
    
    await render_progress_history(user, tracker)


async def run_leaderboard_view():
    """Run leaderboard view application"""
    await initialize_database()
    tracker = HybridProgressTracker()
    if st.session_state.db_initialized:
        tracker.db_tracker = UserProgressTrackerDB()
    
    await render_leaderboard(tracker)


async def render_dashboard(user_data, tracker):
    """Render main dashboard with BANS stats like original streamlit_app.py"""
    # Header with logout button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div class='main-header'>🎯 Prompt Engineering Training</div>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", type="secondary"):
            # Clear all session state
            for key in ['authenticated', 'user_data', 'auth_step', 'proceed_app', 'view_progress_app', 'view_leaderboard_app']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_user = None
            st.rerun()
    
    st.markdown(f"### Welcome back, **{user_data.username}**! 👋")
    
    # Get user stats using the tracker
    stats = await tracker.get_user_stats(user_data.ldap_id)
    
    # User stats cards in BANS format (like original streamlit_app.py)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    # Calculate average score
    avg_score = stats['avg_score'] if stats['avg_score'] > 0 else (stats['total_score'] / stats['attempts'] if stats['attempts'] > 0 else 0)
    
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
        status_level = stats.get('current_skill_level', 'beginner').title()
        st.markdown(f"""
        <div class='score-card'>
            <h2>{status_level}</h2>
            <p>Skill Level</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        badges_count = len(stats.get('badges', []))
        st.markdown(f"""
        <div class='score-card'>
            <h2>{badges_count}</h2>
            <p>Badges Earned</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display badges if any
    badges = stats.get('badges', [])
    if badges:
        st.markdown("### 🏆 Your Badges")
        badge_html = " ".join([f"<span class='badge'>{badge}</span>" for badge in badges])
        st.markdown(badge_html, unsafe_allow_html=True)
    
    st.markdown("---")

async def render_practice_mode(user_data, tracker):
    """Render practice mode using original UI design"""
    stats = await tracker.get_user_stats(user_data.ldap_id)
    
    st.markdown("## 📝 Practice Mode")
    
    # Scenario generation mode selection (removed mixed mode)
    st.markdown("### 🎲 Scenario Generation")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        generation_mode = st.selectbox(
            "Choose scenario source:",
            ["preset", "ai"],
            format_func=lambda x: {
                "preset": "📚 Preset Scenarios (Curated by experts)",
                "ai": "🤖 AI-Generated Scenarios (Fresh & dynamic)"
            }[x],
            index=["preset", "ai"].index(st.session_state.scenario_generation_mode),
            help="Preset scenarios are curated examples. AI-generated scenarios use preset scenarios as few-shot examples."
        )
        st.session_state.scenario_generation_mode = generation_mode
    
    # Display scenario statistics
    if generation_mode == "preset":
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
            index=["beginner", "intermediate", "advanced"].index(stats.get('current_skill_level', 'beginner'))
        )
    
    with col2:
        scenario_button_text = {
            "preset": "Get Random Preset Scenario",
            "ai": "🤖 Generate AI Scenario"
        }[generation_mode]
        
        if st.button(scenario_button_text, type="primary", use_container_width=True):
            with st.spinner("🤖 Generating scenario..." if generation_mode == "ai" else "Loading scenario..."):
                try:
                    if generation_mode == "preset":
                        st.session_state.current_scenario = get_random_scenario_by_level(selected_level)
                    else:  # ai
                        st.session_state.current_scenario = await get_ai_scenario_by_level(selected_level)
                    
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
    
    # Display current scenario (using original design)
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
            if st.button("Submit for Evaluation", type="primary", use_container_width=True):
                if user_prompt.strip():
                    with st.spinner("🤖 AI is evaluating your prompt..."):
                        try:
                            # Run async evaluation
                            evaluation = await evaluate_user_prompt_async(user_prompt, scenario)
                            
                            # Record attempt
                            await tracker.record_attempt(
                                user_data.ldap_id,
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
        
        with col2:
            new_scenario_text = {
                "preset": "Try Different Preset Scenario",
                "ai": "🤖 Generate New AI Scenario"
            }[generation_mode]
            
            if st.button(new_scenario_text, use_container_width=True):
                st.session_state.current_scenario = None
                st.session_state.show_results = False
                st.rerun()
        
        # Display results (using original design)
        if st.session_state.show_results and 'evaluation_results' in st.session_state:
            evaluation = st.session_state.evaluation_results
            
            st.markdown("---")
            st.markdown("## 📊 Evaluation Results")
            
            # Score display (original design)
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
            
            # Detailed scores (original design)
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
                    "ai": "🤖 Generate New AI Scenario"
                }[generation_mode]
                
                if st.button(next_scenario_text, type="primary", use_container_width=True):
                    st.session_state.current_scenario = None
                    st.session_state.show_results = False
                    st.rerun()


async def render_progress_history(user_data, tracker):
    """Render progress history using session data"""
    stats = await tracker.get_user_stats(user_data.ldap_id)
    
    st.markdown("## 📈 Your Progress History")
    
    if stats.get('history'):
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


async def render_leaderboard(tracker):
    """Render enhanced leaderboard with Top 20 per group and Top 20 overall side by side"""
    st.markdown("## 🏆 Leaderboard")
    
    # Get multi-group leaderboard data
    multi_leaderboard = await tracker.get_multi_group_leaderboard(limit_per_group=20)
    
    if not multi_leaderboard:
        st.info("No entries yet. Be the first to complete a challenge!")
        return
    
    # Create two main columns for side-by-side display
    col1, col2 = st.columns([1, 1])
    
    # Left column: Overall Top 20 (All Groups)
    with col1:
        st.markdown("### 🌐 Top 20 Overall")
        
        all_groups_data = multi_leaderboard.get('all_groups', [])
        if all_groups_data:
            for i, entry in enumerate(all_groups_data[:20], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                
                row_col1, row_col2, row_col3, row_col4, row_col5 = st.columns([0.5, 2, 2, 1.5, 1])
                with row_col1:
                    st.markdown(f"**{medal}**")
                with row_col2:
                    st.markdown(f"**{entry['username']}**")
                with row_col3:
                    st.markdown(f"*{entry['user_group'].title()}*")
                with row_col4:
                    st.markdown(f"**{entry['avg_score']:.1f}**")
                with row_col5:
                    badges_count = len(entry.get('badges', [])) if isinstance(entry.get('badges', []), list) else entry.get('total_badges', 0)
                    st.markdown(f"🏅**{badges_count}**")
                
                if i < len(all_groups_data[:20]):  # Don't show separator after last item
                    st.markdown("---")
        else:
            st.info("No overall leaderboard data yet")
    
    # Right column: Per-group Top 20s
    with col2:
        st.markdown("### 👥 Top 20 by Group")
        
        # Group selection dropdown
        group_names = [key for key in multi_leaderboard.keys() if key != 'all_groups']
        
        if group_names:
            selected_group = st.selectbox(
                "Select Group to View:",
                group_names,
                key="group_leaderboard_selector"
            )
            
            group_data = multi_leaderboard.get(selected_group, [])
            
            if group_data:
                st.markdown(f"**{selected_group.title()} Group**")
                
                for i, entry in enumerate(group_data, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    
                    row_col1, row_col2, row_col3, row_col4, row_col5 = st.columns([0.5, 2, 1.5, 1.5, 1])
                    with row_col1:
                        st.markdown(f"**{medal}**")
                    with row_col2:
                        st.markdown(f"**{entry['username']}**")
                    with row_col3:
                        st.markdown(f"**{entry['avg_score']:.1f}**")
                    with row_col4:
                        st.markdown(f"**{entry['current_skill_level'].title()}**")
                    with row_col5:
                        badges_count = len(entry.get('badges', [])) if isinstance(entry.get('badges', []), list) else entry.get('total_badges', 0)
                        st.markdown(f"🏅**{badges_count}**")
                    
                    if i < len(group_data):  # Don't show separator after last item
                        st.markdown("---")
                
                # Show group stats in expander
                with st.expander(f"📊 {selected_group.title()} Group Statistics"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Players", len(group_data))
                    with col2:
                        avg_score = sum(entry['avg_score'] for entry in group_data) / len(group_data)
                        st.metric("Group Average", f"{avg_score:.1f}")
                    with col3:
                        total_attempts = sum(entry['total_attempts'] for entry in group_data)
                        st.metric("Total Attempts", total_attempts)
            else:
                st.info(f"No players in {selected_group} group yet")
        else:
            st.info("No groups created yet")
    
    # Summary section below
    st.markdown("---")
    st.markdown("### 📊 Leaderboard Summary")
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        total_users = 0
        total_attempts = 0
        groups = set()
        
        if multi_leaderboard:
            for group_name, group_data in multi_leaderboard.items():
                if group_name != 'all_groups':
                    total_users += len(group_data)
                    total_attempts += sum(entry.get('total_attempts', 0) for entry in group_data)
                    groups.add(group_name)
        
        with col1:
            st.metric("Total Active Users", total_users)
        with col2:
            st.metric("Total Attempts", total_attempts)
        with col3:
            st.metric("Active Groups", len(groups))
        with col4:
            if total_users > 0:
                st.metric("Avg Score Overall", "TBD")  # Can calculate if needed
            else:
                st.metric("Avg Score Overall", "N/A")
                
    except Exception as e:
        st.error(f"Could not fetch leaderboard statistics: {str(e)}")


async def render_admin_panel(tracker):
    """Render admin panel with CSV export and database reset functionality"""
    st.markdown("## ⚙️ Admin Panel")
    
    # Admin password protection
    admin_password = st.text_input("Admin Password", type="password", placeholder="Enter admin password")
    
    if admin_password != "PIP-ADMIN":
        st.warning("🔒 Please enter the correct admin password to access admin functions")
        return
    
    st.success("✅ Admin access granted")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Data Export")
        
        # Group selection for export
        group_options = ["All Groups"] + ["GBS", "T&E", "PCC"]
        selected_group = st.selectbox("Select Group to Export", group_options)
        
        if st.button("📥 Export User Data to CSV", use_container_width=True, type="primary"):
            try:
                # Get multi-group leaderboard data for export
                if selected_group == "All Groups":
                    export_data = await tracker.get_multi_group_leaderboard(limit_per_group=1000)
                else:
                    export_data = await tracker.get_leaderboard(top_n=1000, group=selected_group)
                
                if not export_data:
                    st.warning("No data to export")
                    return
                
                # Convert to CSV format
                import pandas as pd
                from datetime import datetime
                
                # Create timestamp filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"user_progress_export_{selected_group.lower().replace(' ', '_')}_{timestamp}.csv"
                
                # Prepare data for CSV
                rows = []
                
                if isinstance(export_data, dict):
                    # Multi-group export
                    for group_name, leaderboard_entries in export_data.items():
                        if group_name == 'all_groups':
                            continue
                        for entry in leaderboard_entries:
                            row = {
                                'username': entry['username'],
                                'ldap_id': entry.get('ldap_id', ''),
                                'user_group': group_name,
                                'avg_score': entry['avg_score'],
                                'total_attempts': entry['total_attempts'],
                                'current_skill_level': entry['current_skill_level'],
                                'total_badges': entry.get('total_badges', 0)
                            }
                            rows.append(row)
                else:
                    # Single group export
                    for entry in export_data:
                        row = {
                            'username': entry['username'],
                            'ldap_id': entry.get('ldap_id', ''),
                            'user_group': entry.get('user_group', selected_group),
                            'avg_score': entry['avg_score'],
                            'total_attempts': entry['total_attempts'],
                            'current_skill_level': entry['current_skill_level'],
                            'total_badges': entry.get('total_badges', 0)
                        }
                        rows.append(row)
                
                if rows:
                    df = pd.DataFrame(rows)
                    df.to_csv(filename, index=False)
                    st.success(f"✅ Data exported successfully to: `{filename}`")
                    
                    # Show preview
                    st.markdown("### 👀 Preview of Exported Data")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Quick stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Records Exported", len(df))
                    with col2:
                        avg_score = df['avg_score'].mean()
                        st.metric("Average Score", f"{avg_score:.1f}")
                    with col3:
                        st.metric("Total Attempts", df['total_attempts'].sum())
                else:
                    st.warning("No data to export")
                    
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        st.markdown("### 🗄️ Database Management")
        
        st.markdown("**⚠️ DANGER ZONE**")
        
        confirm_reset = st.checkbox("I understand this will delete ALL data")
        
        if confirm_reset and st.button("🗑️ Reset Database", use_container_width=True, type="secondary"):
            st.error("🚨 Database Reset functionality requires implementation of database table truncation")
            st.info("This feature would need to be implemented in the database service layer")
            
            # Note: In a real production environment, you would implement:
            # await tracker.reset_all_data()
    
    # Additional admin info
    st.markdown("---")
    st.markdown("### 📋 Admin Information")
    
    try:
        # Get system stats
        all_data = await tracker.get_multi_group_leaderboard(limit_per_group=100)
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_users = 0
        total_attempts = 0
        groups = set()
        
        if all_data:
            for group_data in all_data.values():
                total_users += len(group_data)
                total_attempts += sum(entry.get('total_attempts', 0) for entry in group_data)
                for entry in group_data[:1]:  # Just get groups from each type
                    groups.add(entry.get('user_group', 'Unknown'))
        
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Total Attempts", total_attempts)
        with col3:
            st.metric("Active Groups", len(groups))
        with col4:
            if total_users > 0:
                st.metric("Avg Score System", "TBD")
            else:
                st.metric("Avg Score System", "N/A")
                
    except Exception as e:
        st.error(f"Could not fetch admin statistics: {str(e)}")


async def run_main_application():
    """Run the main training application for Authenticated users"""
    require_authentication()
    
    # Get authenticated user
    user = get_current_user()
    if not user:
        st.error("Authentication error. Please login again.")
        await run_authentication_flow()
        return
    
    # Initialize hybrid tracker
    tracker = HybridProgressTracker()
    # Use database tracker if initialization was successful
    if st.session_state.get('db_initialized', False):
        tracker.db_tracker = UserProgressTrackerDB()
    
    # Render dashboard
    await render_dashboard(user, tracker)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        page = st.radio(
            "Go to:",
            ["Dashboard", "Practice Mode", "Leaderboard", "Progress History", "Admin Panel"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats in sidebar
        stats = await tracker.get_user_stats(user.ldap_id)
        st.markdown("### 📊 Quick Stats")
        attempts = stats.get('attempts', 0)
        total_score = stats.get('total_score', 0)
        avg_score = stats.get('avg_score', 0)
        st.metric("Attempts", attempts)
        # Use the calculated average from stats if available, otherwise calculate manually
        display_avg = avg_score if avg_score > 0 else (total_score / attempts if attempts > 0 else 0)
        st.metric("Avg Score", f"{display_avg:.1f}")
        st.metric("Skill Level", stats.get('current_skill_level', 'beginner').title())
        
        st.markdown("---")
        st.markdown("### ℹ️ About Prompt Quest")
        st.info("Gamified Prompt Engineering Training for Microsoft 365 Copilot. Powered by Google ADK and Vertex AI.")
    
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
        await render_practice_mode(user, tracker)
    
    elif page == "Leaderboard":
        await render_leaderboard(tracker)
    
    elif page == "Progress History":
        await render_progress_history(user, tracker)
    
    elif page == "Admin Panel":
        await render_admin_panel(tracker)


# Removed duplicate main function - using streamlit_main instead


# Helper function to run async functions in Streamlit
def run_async(coro):
    """Run async function in Streamlit"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception as e:
        st.error(f"Async operation failed: {e}")
        return None
    finally:
        try:
            loop.close()
        except:
            pass

# Main application entry point
def main():
    """Streamlit main function"""
    
    # Try to initialize database once at startup
    if not st.session_state.get('startup_complete', False):
        st.info("🚀 Starting Prompt Training Lab (Database Edition)...")
        
        # Run database initialization
        init_result = run_async(initialize_database())
        st.session_state.startup_complete = True
        
        if st.session_state.get('db_error'):
            st.warning("⚠️ Database unavailable - running in limited mode")
    
    # Check if user is authenticated
    if not is_logged_in():
        # Show authentication flow
        run_async(run_authentication_flow())
    else:
        # User is logged in - show main training interface
        run_async(run_main_application())

# Streamlit will call this function
if __name__ == "__main__":
    main()