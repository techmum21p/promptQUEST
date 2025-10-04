"""
Setup Verification Script
Run this to verify your installation is correct before running the main app
Usage: python test_setup.py
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def test_python_version():
    """Test Python version"""
    print_header("Testing Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 9:
        print_success("Python version is compatible (3.9+)")
        return True
    else:
        print_error("Python 3.9 or higher is required")
        return False

def test_imports():
    """Test required imports"""
    print_header("Testing Required Packages")
    
    all_success = True
    
    # Test Google ADK
    try:
        from google.adk.agents import Agent
        print_success("google-adk installed correctly")
    except ImportError as e:
        print_error(f"google-adk not found: {e}")
        all_success = False
    
    # Test Streamlit
    try:
        import streamlit
        print_success(f"streamlit installed correctly (v{streamlit.__version__})")
    except ImportError as e:
        print_error(f"streamlit not found: {e}")
        all_success = False
    
    # Test dotenv
    try:
        from dotenv import load_dotenv
        print_success("python-dotenv installed correctly")
    except ImportError as e:
        print_error(f"python-dotenv not found: {e}")
        all_success = False
    
    # Test Google Cloud
    try:
        from google.cloud import aiplatform
        print_success("google-cloud-aiplatform installed correctly")
    except ImportError as e:
        print_warning(f"google-cloud-aiplatform not found (optional for AI Studio): {e}")
    
    # Test google-genai
    try:
        import google.genai
        print_success("google-genai installed correctly")
    except ImportError as e:
        print_error(f"google-genai not found: {e}")
        all_success = False
    
    return all_success

def test_env_file():
    """Test .env file exists and has required variables"""
    print_header("Testing Environment Configuration")
    
    if not Path(".env").exists():
        print_error(".env file not found")
        print_warning("Copy .env.example to .env and configure your credentials")
        return False
    
    print_success(".env file exists")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").upper()
    
    if use_vertex == "TRUE":
        print("Using Vertex AI configuration")
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        
        if project:
            print_success(f"Project ID configured: {project}")
        else:
            print_error("GOOGLE_CLOUD_PROJECT not set in .env")
            return False
        
        if location:
            print_success(f"Location configured: {location}")
        else:
            print_error("GOOGLE_CLOUD_LOCATION not set in .env")
            return False
    
    elif use_vertex == "FALSE":
        print("Using Google AI Studio configuration")
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if api_key:
            print_success(f"API Key configured (length: {len(api_key)})")
        else:
            print_error("GOOGLE_API_KEY not set in .env")
            return False
    else:
        print_error("GOOGLE_GENAI_USE_VERTEXAI not properly set in .env")
        print_warning("Set to TRUE for Vertex AI or FALSE for AI Studio")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print_header("Testing File Structure")
    
    required_files = [
        "prompt_training_app.py",
        "streamlit_app.py",
        "requirements.txt",
        ".env"
    ]
    
    all_exist = True
    for filename in required_files:
        if Path(filename).exists():
            print_success(f"{filename} exists")
        else:
            print_error(f"{filename} not found")
            all_exist = False
    
    # Check optional files
    optional_files = ["README.md", "SETUP_GUIDE.md", "QUICK_REFERENCE.md"]
    for filename in optional_files:
        if Path(filename).exists():
            print_success(f"{filename} exists (optional)")
        else:
            print_warning(f"{filename} not found (optional)")
    
    return all_exist

def test_google_cloud_auth():
    """Test Google Cloud authentication"""
    print_header("Testing Google Cloud Authentication")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").upper()
    
    if use_vertex != "TRUE":
        print_warning("Skipping (not using Vertex AI)")
        return True
    
    # Check if gcloud is installed
    import subprocess
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("gcloud CLI is installed")
        else:
            print_error("gcloud CLI not working properly")
            return False
    except FileNotFoundError:
        print_error("gcloud CLI not found")
        print_warning("Install from: https://cloud.google.com/sdk/docs/install")
        return False
    except subprocess.TimeoutExpired:
        print_error("gcloud command timed out")
        return False
    
    # Check authentication
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            print_success("Application Default Credentials configured")
            return True
        else:
            print_error("Application Default Credentials not configured")
            print_warning("Run: gcloud auth application-default login")
            return False
    except subprocess.TimeoutExpired:
        print_error("Authentication check timed out")
        return False

def test_agent_creation():
    """Test creating a simple agent"""
    print_header("Testing Agent Creation")
    
    try:
        from google.adk.agents import Agent
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Create a test agent
        test_agent = Agent(
            name="test_agent",
            model="gemini-2.0-flash",
            description="Test agent for verification",
            instruction="You are a test assistant."
        )
        
        print_success("Agent created successfully")
        print(f"   Agent name: {test_agent.name}")
        print(f"   Model: {test_agent.model}")
        return True
        
    except Exception as e:
        print_error(f"Failed to create agent: {e}")
        return False

def test_app_imports():
    """Test importing from the main app"""
    print_header("Testing Application Imports")
    
    try:
        # Test importing main app
        sys.path.insert(0, os.getcwd())
        
        from prompt_training_app import (
            PromptEvaluatorAgent,
            CopilotScenarioGenerator,
            UserProgressTracker
        )
        
        print_success("prompt_training_app.py imports work")
        
        # Test creating instances
        tracker = UserProgressTracker(storage_file="test_progress.json")
        print_success("UserProgressTracker instantiated")
        
        # Clean up test file
        if Path("test_progress.json").exists():
            Path("test_progress.json").unlink()
        
        # Test scenario generator
        scenarios = CopilotScenarioGenerator.get_scenarios()
        print_success(f"CopilotScenarioGenerator works ({len(scenarios['beginner'])} beginner scenarios)")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to import application modules: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_compatibility():
    """Test Streamlit compatibility"""
    print_header("Testing Streamlit Compatibility")
    
    try:
        import streamlit as st
        
        # Check version
        version = st.__version__
        major, minor = map(int, version.split('.')[:2])
        
        if major >= 1 and minor >= 28:
            print_success(f"Streamlit version {version} is compatible")
            return True
        else:
            print_warning(f"Streamlit version {version} may have compatibility issues")
            print_warning("Recommended: 1.28.0 or higher")
            return True
            
    except Exception as e:
        print_error(f"Streamlit compatibility check failed: {e}")
        return False

def run_full_integration_test():
    """Run a full integration test"""
    print_header("Running Integration Test")
    print_warning("This test will make an API call to Gemini (may incur small cost)")
    
    response = input("Run integration test? (y/n): ")
    if response.lower() != 'y':
        print_warning("Skipping integration test")
        return True
    
    try:
        import asyncio
        from prompt_training_app import (
            PromptEvaluatorAgent,
            CopilotScenarioGenerator
        )
        
        print("\nCreating evaluator agent...")
        evaluator = PromptEvaluatorAgent()
        print_success("Evaluator created")
        
        print("\nGetting test scenario...")
        scenario = CopilotScenarioGenerator.get_random_scenario("beginner")
        print_success(f"Got scenario: {scenario['title']}")
        
        print("\nEvaluating test prompt (this may take 10-30 seconds)...")
        test_prompt = "Please summarize the email thread and list all action items with their owners."
        
        async def run_test():
            result = await evaluator.evaluate_prompt(test_prompt, scenario)
            return result
        
        evaluation = asyncio.run(run_test())
        
        if evaluation and 'total_score' in evaluation:
            print_success(f"Integration test passed! Score: {evaluation['total_score']}/100")
            print(f"   Feedback: {evaluation.get('feedback', 'N/A')[:100]}...")
            return True
        else:
            print_error("Integration test failed - unexpected response format")
            return False
            
    except Exception as e:
        print_error(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(results):
    """Print summary of all tests"""
    print_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print()
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    
    if failed_tests == 0:
        print_success("All tests passed! Your setup is ready. ✨")
        print("\nNext steps:")
        print("  1. Run: streamlit run streamlit_app.py")
        print("  2. Open http://localhost:8501 in your browser")
        print("  3. Start training!")
        return True
    else:
        print_error(f"{failed_tests} test(s) failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Missing packages: pip install -r requirements.txt")
        print("  • Auth issues: gcloud auth application-default login")
        print("  • Missing .env: cp .env.example .env (then configure)")
        return False

def main():
    """Run all tests"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     Prompt Engineering Training App - Setup Test         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Run all tests
    results["Python Version"] = test_python_version()
    results["Required Packages"] = test_imports()
    results["File Structure"] = test_file_structure()
    results["Environment Config"] = test_env_file()
    results["Google Cloud Auth"] = test_google_cloud_auth()
    results["Agent Creation"] = test_agent_creation()
    results["Application Imports"] = test_app_imports()
    results["Streamlit Compatibility"] = test_streamlit_compatibility()
    
    # Optional integration test
    if all(results.values()):
        results["Integration Test"] = run_full_integration_test()
    else:
        print_warning("\nSkipping integration test due to previous failures")
        results["Integration Test"] = None
    
    # Print summary
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())