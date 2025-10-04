#!/usr/bin/env python3
"""
Simplified launcher for the database-enabled Streamlit app
This wrapper properly handles async functions for Streamlit
"""

import subprocess
import sys
import os

def main():
    """Launch the database Streamlit app with proper configuration"""
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Set Streamlit configuration for better async handling
    env = os.environ.copy()
    env['STREAMLIT_SERVER_PORT'] = '8501'
    env['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'true'
    env['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    print("🚀 Starting Prompt Training Lab (Database Edition)...")
    print("📁 Working directory:", script_dir)
    print("🔧 Streamlit will handle async functions internally")
    print("---")
    
    try:
        # Run Streamlit with the database app
        result = subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'streamlit_app_db.py',
            '--server.headless', 'true',
            '--server.address', '0.0.0.0',
            '--server.port', '8501'
        ], env=env)
        
        return result.returncode
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
