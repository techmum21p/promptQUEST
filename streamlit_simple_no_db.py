"""
Simplified Streamlit app without database dependency - for testing
This version avoids async issues completely by using session state
"""

import streamlit as st
import asyncio
from datetime import datetime
from prompt_training_app import (
    evaluate_user_prompt_async,
    get_random_scenario_by_level,
    get_scenario_statistics
)

st.set_page_config(
    page_title="Prompt Training (Simple)",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Prompt Training Lab - Simple Version")

# Initialize session state
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'stats' not in st.session_state:
    st.session_state.stats = {'attempts': 0, 'total': 0, 'avg': 0}
if 'scenario' not in st.session_state:
    st.session_state.scenario = None

# Authentication
if not st.session_state.user_logged_in:
    st.header("Login")
    username = st.text_input("Username:")
    if st.button("Login"):
        if username:
            st.session_state.user_logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Enter a username")

# Main app
if st.session_state.user_logged_in:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"Welcome, {st.session_state.username}!")
    with col2:
        if st.button("Logout"):
            st.session_state.user_logged_in = False
            st.session_state.username = None
            st.rerun()
    
    # Stats display
    stats = st.session_state.stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Attempts", stats['attempts'])
    with col2:
        st.metric("Total Score", stats['total'])
    with col3:
        avg = stats['total'] / stats['attempts'] if stats['attempts'] > 0 else 0
        st.metric("Average", f"{avg:.1f}")
    
    st.divider()
    
    # Scenario section
    col1, col2 = st.columns([3, 1])
    with col1:
        level = st.selectbox("Level:", ["beginner", "intermediate", "advanced"])
    with col2:
        if st.button("Get Scenario"):
            st.session_state.scenario = get_random_scenario_by_level(level)
            st.rerun()
    
    # Show scenario
    if st.session_state.scenario:
        scenario = st.session_state.scenario
        st.markdown(f"### 📋 {scenario['title']}")
        st.markdown(f"**Product:** {scenario['product']}")
        st.markdown(f"**Description:** {scenario['description']}")
        st.markdown(f"**Goal:** {scenario['goal']}")
        
        if st.expander("Show hints"):
            for i, hint in enumerate(scenario['hints'], 1):
                st.write(f"{i}. {hint}")
        
        if st.expander("Show example"):
            st.success(scenario['example_good'])
        
        # Prompt input
        prompt = st.text_area("Write your prompt:", height=100)
        
        if st.button("Submit"):
            if prompt:
                with st.spinner("Evaluating..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        evaluation = loop.run_until_complete(
                            evaluate_user_prompt_async(prompt, scenario)
                        )
                        loop.close()
                        
                        # Update stats
                        score = evaluation['total_score']
                        stats['attempts'] += 1
                        stats['total'] += score
                        avg = stats['total'] / stats['attempts']
                        
                        # Show results
                        st.success(f"Score: {score}/100")
                        st.markdown("**Feedback:**")
                        st.info(evaluation['feedback'])
                        
                        if evaluation.get('strengths'):
                            st.markdown("**Strengths:**")
                            for strength in evaluation['strengths']:
                                st.write(f"✅ {strength}")
                        
                        if evaluation.get('improvements'):
                            st.markdown("**Areas for Improvement:**")
                            for improvement in evaluation['improvements']:
                                st.write(f"⚠️ {improvement}")
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Enter a prompt")
