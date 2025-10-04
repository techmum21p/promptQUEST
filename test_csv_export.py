#!/usr/bin/env python3
"""
Test script to verify CSV export functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompt_training_app import UserProgressTracker

def test_csv_export():
    """Test the CSV export functionality"""
    print("🧪 Testing CSV Export Functionality...")
    
    # Initialize tracker with existing data
    tracker = UserProgressTracker()
    
    # Get summary
    summary = tracker.get_export_summary()
    print(f"📊 Data Summary:")
    print(f"   Total Users: {summary['total_users']}")
    print(f"   Active Users: {summary['active_users']}")
    print(f"   Total Attempts: {summary['total_attempts']}")
    print(f"   Average Score: {summary['avg_score_all_users']}")
    
    if summary['total_users'] > 0:
        # Test export
        print("\n📥 Testing export...")
        filename = tracker.export_to_csv("test_export.csv")
        
        if filename:
            print(f"✅ Export successful: {filename}")
            
            # Verify the file exists and has content
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"📁 File size: {file_size} bytes")
                
                # Try to read with pandas
                try:
                    import pandas as pd
                    df = pd.read_csv(filename)
                    print(f"📊 Records in CSV: {len(df)}")
                    print(f"📋 Columns: {list(df.columns)}")
                    
                    # Show first few rows
                    print("\n👀 Sample data:")
                    print(df.head(3).to_string())
                    
                    # Clean up test file
                    os.remove(filename)
                    print(f"\n🧹 Cleaned up test file: {filename}")
                    
                except Exception as e:
                    print(f"❌ Error reading CSV: {str(e)}")
            else:
                print("❌ Export file not found")
        else:
            print("❌ Export returned None - no data to export")
    else:
        print("ℹ️  No users found - testing with empty data")
        filename = tracker.export_to_csv("empty_test.csv")
        if filename is None:
            print("✅ Correctly handled empty data case")
        else:
            print(f"⚠️  Unexpected: export created file for empty data: {filename}")
    
    print("\n🎉 CSV Export test completed!")

if __name__ == "__main__":
    test_csv_export()