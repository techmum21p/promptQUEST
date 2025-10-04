"""
Simple Streamlit wrapper that properly handles async functions
This avoids the complex event loop issues
"""

import streamlit as st
import asyncio
from streamlit_app_db import (
    run_authentication_flow,
    run_main_application,
    run_progress_view,
    run_leaderboard_view,
    initialize_database,
    is_logged_in
)

def run_app():
    """Simple synchronous wrapper for the async app"""
    
    # Show a loading spinner while initializing
    with st.spinner("Initializing..."):
        try:
            # Create a new event loop for this run
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Check if user is authenticated
            if not is_logged_in():
                # Run authentication flow
                loop.run_until_complete(run_authentication_flow())
            else:
                # Run main application
                loop.run_until_complete(run_main_application())
                
        except Exception as e:
            st.error(f"Application error: {e}")
            st.exception(e)
        finally:
            # Clean shutdown
            try:
                loop.close()
            except:
                pass

# Run the app
if __name__ == "__main__":
    run_app()
