"""
Quick setup checker for PostgreSQL Prompt Training App
"""

import os
from pathlib import Path


def check_setup():
    """Check if setup environment is ready"""
    
    print("🔍 Checking setup environment...")
    print("=" * 40)
    
    issues = []
    
    # Check environment file
    env_file = Path(".env")
    env_example = Path("env-example-db.env")
    
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("❌ .env file missing")
        if env_example.exists():
            print("   💡 Copy env-example-db.env to .env")
        issues.append("Missing .env file")
    
    # Check environment variables
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            required_vars = [
                'POSTGRES_HOST',
                'POSTGRES_PORT', 
                'POSTGRES_DB',
                'POSTGRES_USER',
                'POSTGRES_PASSWORD'
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
                issues.append("Missing environment variables")
            else:
                print("✅ Environment variables configured")
                
        except ImportError:
            print("⚠️  python-dotenv not installed (optional)")
    
    # Check files
    required_files = [
        'database/schema.sql',
        'setup_database.py', 
        'prompt_training_app_db.py',
        'streamlit_app_db.py',
        'requirements-db.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        issues.append("Missing files")
    
    # Check PostgreSQL availability
    import subprocess
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ PostgreSQL available: {result.stdout.strip()}")
        else:
            print("❌ PostgreSQL not found in PATH")
            issues.append("PostgreSQL not available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ PostgreSQL (psql) command not found")
        issues.append("PostgreSQL not available")
    
    print("\n" + "=" * 40)
    if issues:
        print("❌ Setup issues found:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n💡 Run: python3 setup_database.py --action setup")
        return False
    else:
        print("✅ Setup environment looks good!")
        print("💡 Ready to run: python3 setup_database.py --action setup")
        return True


if __name__ == "__main__":
    check_setup()
