#!/usr/bin/env python3
"""
Test script to verify that strengths and improvements are properly recorded and exported
"""

import json
import os
from prompt_training_app import UserProgressTracker

def test_strengths_improvements_recording():
    """Test that strengths and improvements are properly stored and exported"""
    print("🧪 Testing Strengths & Improvements Recording")
    print("=" * 60)
    
    # Create a test tracker with a temporary file
    test_file = "test_strengths_improvements.json"
    tracker = UserProgressTracker(test_file)
    
    try:
        # Test data
        test_user = "test_user_si"
        test_scenario_id = "i1"
        test_score = 88
        test_prompt = "Analyze Q1-Q3 sales data to identify top-performing regions and products. Create visualizations showing monthly trends and regional comparisons."
        test_evaluation = {
            "clarity_score": 22,
            "specificity_score": 23,
            "structure_score": 21,
            "task_alignment_score": 22,
            "total_score": 88,
            "feedback": "Strong prompt with clear objectives and specific requirements. Good use of action verbs and well-defined scope.",
            "strengths": [
                "Clear action verbs (analyze, identify, create)",
                "Specific data scope (Q1-Q3)",
                "Multiple visualization requirements",
                "Well-defined comparison criteria"
            ],
            "improvements": [
                "Could specify chart types or dashboard format",
                "Consider mentioning target audience",
                "Add timeline or deadline context"
            ]
        }
        
        # Record the attempt with strengths and improvements
        print(f"📝 Recording attempt with strengths and improvements...")
        tracker.record_attempt(test_user, test_scenario_id, test_score, test_evaluation, test_prompt)
        
        # Retrieve user stats
        stats = tracker.get_user_stats(test_user)
        
        # Verify the data was recorded correctly
        print(f"\n✅ User Stats Retrieved:")
        print(f"   - Username: {test_user}")
        print(f"   - Attempts: {stats['attempts']}")
        print(f"   - Total Score: {stats['total_score']}")
        
        # Check the history entry
        if stats['history']:
            history_entry = stats['history'][0]
            eval_data = history_entry['evaluation']
            
            print(f"\n📋 History Entry Details:")
            print(f"   - Scenario ID: {history_entry['scenario_id']}")
            print(f"   - Score: {history_entry['score']}")
            print(f"   - User Prompt: {history_entry.get('user_prompt', 'NOT FOUND')[:50]}...")
            
            # Check strengths
            strengths = eval_data.get('strengths', [])
            print(f"\n✅ Strengths ({len(strengths)} items):")
            for i, strength in enumerate(strengths[:3], 1):  # Show first 3
                print(f"   {i}. {strength}")
            
            # Check improvements
            improvements = eval_data.get('improvements', [])
            print(f"\n🔧 Improvements ({len(improvements)} items):")
            for i, improvement in enumerate(improvements[:3], 1):  # Show first 3
                print(f"   {i}. {improvement}")
            
            if strengths and improvements:
                print(f"\n🎉 SUCCESS: Strengths and improvements correctly recorded!")
            else:
                print(f"\n❌ FAILED: Missing strengths or improvements")
                print(f"   Strengths found: {len(strengths)}")
                print(f"   Improvements found: {len(improvements)}")
        
        # Test CSV export with strengths and improvements
        print(f"\n📊 Testing CSV Export with Strengths & Improvements...")
        export_filename = tracker.export_to_csv("test_si_export.csv")
        
        if export_filename and os.path.exists(export_filename):
            print(f"✅ CSV Export created: {export_filename}")
            
            # Read and verify CSV content
            try:
                import pandas as pd
                df = pd.read_csv(export_filename)
                
                # Check for required columns
                required_columns = ['user_prompt', 'strengths', 'improvements']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if not missing_columns:
                    print(f"✅ CSV contains all required columns: {required_columns}")
                    
                    # Check if our test data is in the CSV
                    row = df.iloc[0]  # First row should be our test data
                    
                    print(f"\n📄 CSV Content Verification:")
                    print(f"   - User Prompt: {str(row['user_prompt'])[:50]}...")
                    print(f"   - Strengths: {str(row['strengths'])[:60]}...")
                    print(f"   - Improvements: {str(row['improvements'])[:60]}...")
                    
                    # Verify strengths are properly joined
                    if 'Clear action verbs' in str(row['strengths']):
                        print(f"✅ Strengths properly exported and joined")
                    else:
                        print(f"❌ Strengths not properly exported")
                    
                    # Verify improvements are properly joined  
                    if 'Could specify chart types' in str(row['improvements']):
                        print(f"✅ Improvements properly exported and joined")
                    else:
                        print(f"❌ Improvements not properly exported")
                        
                else:
                    print(f"❌ CSV missing required columns: {missing_columns}")
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
        
        # Test with empty strengths/improvements (backward compatibility)
        print(f"\n🔄 Testing empty strengths/improvements...")
        test_evaluation_empty = {
            "clarity_score": 18,
            "specificity_score": 19,
            "structure_score": 17,
            "task_alignment_score": 18,
            "total_score": 72,
            "feedback": "Basic prompt, could use more detail.",
            "strengths": [],  # Empty list
            "improvements": []  # Empty list
        }
        
        tracker.record_attempt(test_user, "b2", 72, test_evaluation_empty, "Simple test prompt")
        
        # Check second entry
        stats_after = tracker.get_user_stats(test_user)
        if len(stats_after['history']) == 2:
            second_entry = stats_after['history'][1]
            eval_data_2 = second_entry['evaluation']
            print(f"✅ Empty strengths/improvements handled correctly")
            print(f"   - Strengths: {eval_data_2.get('strengths', 'MISSING')}")
            print(f"   - Improvements: {eval_data_2.get('improvements', 'MISSING')}")
        
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
    print(f"🏁 Strengths & Improvements Test Complete!")

if __name__ == "__main__":
    test_strengths_improvements_recording()