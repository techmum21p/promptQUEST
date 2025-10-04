#!/usr/bin/env python3
"""
Test script to verify that user prompts are properly recorded in the progress history
"""

import json
import os
from prompt_training_app import UserProgressTracker

def test_user_prompt_recording():
    """Test that user prompts are properly stored and retrieved"""
    print("🧪 Testing User Prompt Recording Functionality")
    print("=" * 60)
    
    # Create a test tracker with a temporary file
    test_file = "test_user_progress.json"
    tracker = UserProgressTracker(test_file)
    
    try:
        # Test data
        test_user = "test_user"
        test_scenario_id = "b1"
        test_score = 85
        test_prompt = "This is a test prompt that should be recorded in the history."
        test_evaluation = {
            "clarity_score": 20,
            "specificity_score": 22,
            "structure_score": 21,
            "task_alignment_score": 22,
            "total_score": 85,
            "feedback": "Good test prompt!",
            "strengths": ["Clear", "Specific"],
            "improvements": ["Add more context"]
        }
        
        # Record the attempt with user prompt
        print(f"📝 Recording attempt with user prompt: '{test_prompt}'")
        tracker.record_attempt(test_user, test_scenario_id, test_score, test_evaluation, test_prompt)
        
        # Retrieve user stats
        stats = tracker.get_user_stats(test_user)
        
        # Verify the data was recorded correctly
        print(f"\n✅ User Stats Retrieved:")
        print(f"   - Username: {test_user}")
        print(f"   - Attempts: {stats['attempts']}")
        print(f"   - Total Score: {stats['total_score']}")
        print(f"   - History Length: {len(stats['history'])}")
        
        # Check the history entry
        if stats['history']:
            history_entry = stats['history'][0]
            print(f"\n📋 History Entry Details:")
            print(f"   - Scenario ID: {history_entry['scenario_id']}")
            print(f"   - Score: {history_entry['score']}")
            print(f"   - User Prompt: '{history_entry.get('user_prompt', 'NOT FOUND')}'")
            print(f"   - Timestamp: {history_entry['timestamp']}")
            
            # Verify the prompt was recorded
            if 'user_prompt' in history_entry and history_entry['user_prompt'] == test_prompt:
                print(f"\n🎉 SUCCESS: User prompt was correctly recorded!")
            else:
                print(f"\n❌ FAILED: User prompt not found or incorrect")
                print(f"   Expected: '{test_prompt}'")
                print(f"   Found: '{history_entry.get('user_prompt', 'NOT FOUND')}'")
        
        # Test CSV export with user prompt
        print(f"\n📊 Testing CSV Export...")
        export_filename = tracker.export_to_csv("test_export.csv")
        
        if export_filename and os.path.exists(export_filename):
            print(f"✅ CSV Export created: {export_filename}")
            
            # Read and verify CSV content
            try:
                import pandas as pd
                df = pd.read_csv(export_filename)
                
                if 'user_prompt' in df.columns:
                    print(f"✅ CSV contains 'user_prompt' column")
                    
                    # Check if our test prompt is in the CSV
                    test_prompt_found = any(df['user_prompt'].str.contains(test_prompt, na=False))
                    if test_prompt_found:
                        print(f"✅ Test prompt found in CSV export")
                    else:
                        print(f"❌ Test prompt not found in CSV export")
                        print(f"CSV user_prompt column: {df['user_prompt'].tolist()}")
                else:
                    print(f"❌ CSV missing 'user_prompt' column")
                    print(f"Available columns: {list(df.columns)}")
                
                # Clean up test export
                os.remove(export_filename)
                print(f"🧹 Cleaned up test export file")
                
            except ImportError:
                print(f"⚠️  pandas not available for CSV verification")
            except Exception as e:
                print(f"❌ Error reading CSV: {str(e)}")
        else:
            print(f"❌ CSV Export failed or file not found")
        
        # Test backward compatibility (attempt without user_prompt)
        print(f"\n🔄 Testing backward compatibility...")
        tracker.record_attempt(test_user, "b2", 75, test_evaluation)  # No user_prompt parameter
        
        stats_after = tracker.get_user_stats(test_user)
        if len(stats_after['history']) == 2:
            second_entry = stats_after['history'][1]
            print(f"✅ Backward compatibility: Entry recorded without user_prompt")
            print(f"   - User prompt field: '{second_entry.get('user_prompt', 'EMPTY')}'")
        else:
            print(f"❌ Backward compatibility failed")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 Cleaned up test file: {test_file}")
    
    print(f"\n" + "=" * 60)
    print(f"🏁 Test Complete!")

if __name__ == "__main__":
    test_user_prompt_recording()