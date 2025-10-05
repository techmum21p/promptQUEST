"""
Migration script to move existing JSON data to PostgreSQL
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from database import create_tables, DatabaseManager, User, UserAttempt, Leaderboard
from postgres_tracker import PostgreSQLUserProgressTracker

def migrate_json_to_postgres(json_file_path: str):
    """Migrate JSON data to PostgreSQL"""
    
    print(f"Starting migration from {json_file_path} to PostgreSQL...")
    
    # Create database tables
    print("Creating database tables...")
    create_tables()
    
    # Load JSON data
    print(f"Loading data from {json_file_path}...")
    if not os.path.exists(json_file_path):
        print(f"Error: JSON file {json_file_path} not found!")
        return False
    
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    if 'users' not in data:
        print("Error: Invalid JSON structure - 'users' key not found!")
        return False
    
    # Initialize tracker
    tracker = PostgreSQLUserProgressTracker()
    
    try:
        # Migrate users
        print("Migrating users...")
        migrated_users = 0
        
        for username, user_data in data['users'].items():
            # Generate LDAP ID (you can modify this logic based on your LDAP system)
            # For now, we'll use a simple mapping or ask for LDAP IDs
            ldap_id = f"ldap_{username.lower()}"  # Placeholder LDAP ID
            
            print(f"Migrating user: {username} (LDAP ID: {ldap_id})")
            
            # Add user
            tracker.add_user(ldap_id, username)
            
            # Migrate attempts/history
            if 'history' in user_data and user_data['history']:
                print(f"  Migrating {len(user_data['history'])} attempts...")
                
                for attempt_data in user_data['history']:
                    try:
                        # Parse timestamp
                        timestamp_str = attempt_data.get('timestamp', '')
                        if timestamp_str:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        else:
                            timestamp = datetime.utcnow()
                        
                        # Extract evaluation data
                        evaluation = attempt_data.get('evaluation', {})
                        
                        # Record attempt
                        tracker.record_attempt(
                            ldap_id=ldap_id,
                            scenario_id=attempt_data.get('scenario_id', ''),
                            score=attempt_data.get('score', 0),
                            evaluation=evaluation,
                            user_prompt=attempt_data.get('user_prompt', '')
                        )
                        
                    except Exception as e:
                        print(f"    Error migrating attempt: {e}")
                        continue
            
            migrated_users += 1
        
        print(f"Successfully migrated {migrated_users} users!")
        
        # Verify migration
        print("Verifying migration...")
        summary = tracker.get_export_summary()
        print(f"Migration summary:")
        print(f"  Total users: {summary['total_users']}")
        print(f"  Total attempts: {summary['total_attempts']}")
        print(f"  Average score: {summary['average_score']}")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False
    
    finally:
        tracker.close()

def interactive_ldap_mapping(json_file_path: str):
    """Interactive migration with LDAP ID mapping"""
    
    print(f"Interactive migration from {json_file_path} to PostgreSQL...")
    
    # Load JSON data
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    if 'users' not in data:
        print("Error: Invalid JSON structure!")
        return False
    
    # Create database tables
    create_tables()
    
    # Initialize tracker
    tracker = PostgreSQLUserProgressTracker()
    
    try:
        print("\nPlease provide LDAP IDs for each user:")
        print("(Press Enter to skip a user, or type 'quit' to exit)")
        
        ldap_mapping = {}
        
        for username in data['users'].keys():
            while True:
                ldap_id = input(f"LDAP ID for user '{username}': ").strip()
                
                if ldap_id.lower() == 'quit':
                    print("Migration cancelled.")
                    return False
                
                if ldap_id == '':
                    print(f"Skipping user '{username}'")
                    break
                
                if ldap_id in ldap_mapping.values():
                    print(f"LDAP ID '{ldap_id}' is already used. Please choose another.")
                    continue
                
                ldap_mapping[username] = ldap_id
                break
        
        if not ldap_mapping:
            print("No users to migrate.")
            return False
        
        # Migrate users with LDAP mapping
        migrated_users = 0
        
        for username, ldap_id in ldap_mapping.items():
            user_data = data['users'][username]
            
            print(f"Migrating user: {username} (LDAP ID: {ldap_id})")
            
            # Add user
            tracker.add_user(ldap_id, username)
            
            # Migrate attempts
            if 'history' in user_data and user_data['history']:
                print(f"  Migrating {len(user_data['history'])} attempts...")
                
                for attempt_data in user_data['history']:
                    try:
                        evaluation = attempt_data.get('evaluation', {})
                        
                        tracker.record_attempt(
                            ldap_id=ldap_id,
                            scenario_id=attempt_data.get('scenario_id', ''),
                            score=attempt_data.get('score', 0),
                            evaluation=evaluation,
                            user_prompt=attempt_data.get('user_prompt', '')
                        )
                        
                    except Exception as e:
                        print(f"    Error migrating attempt: {e}")
                        continue
            
            migrated_users += 1
        
        print(f"\nSuccessfully migrated {migrated_users} users!")
        
        # Show summary
        summary = tracker.get_export_summary()
        print(f"Migration summary:")
        print(f"  Total users: {summary['total_users']}")
        print(f"  Total attempts: {summary['total_attempts']}")
        print(f"  Average score: {summary['average_score']}")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False
    
    finally:
        tracker.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate JSON data to PostgreSQL")
    parser.add_argument("json_file", help="Path to the JSON file to migrate")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Interactive mode for LDAP ID mapping")
    
    args = parser.parse_args()
    
    if args.interactive:
        success = interactive_ldap_mapping(args.json_file)
    else:
        success = migrate_json_to_postgres(args.json_file)
    
    if success:
        print("\nMigration completed successfully!")
    else:
        print("\nMigration failed!")
        sys.exit(1)
