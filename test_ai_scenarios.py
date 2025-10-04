#!/usr/bin/env python3
"""
Test script for AI Scenario Generation
Run this to test the new AI-powered scenario generation functionality
"""

import asyncio
import json
from datetime import datetime
from prompt_training_app import (
    get_ai_scenario_by_level,
    get_mixed_scenario_by_level,
    get_scenario_statistics,
    CopilotScenarioGenerator
)

def print_scenario(scenario, title="Generated Scenario"):
    """Pretty print a scenario"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)
    print(f"ID: {scenario['id']}")
    print(f"Title: {scenario['title']}")
    print(f"Product: {scenario['product']}")
    print(f"\nDescription: {scenario['description']}")
    print(f"\nGoal: {scenario['goal']}")
    print(f"\nContext: {scenario['context']}")
    print(f"\nHints:")
    for i, hint in enumerate(scenario['hints'], 1):
        print(f"  {i}. {hint}")
    print(f"\nExample Good Prompt: {scenario['example_good']}")
    print('='*60)

async def test_ai_generation():
    """Test AI scenario generation for all levels"""
    print("🤖 Testing AI Scenario Generation")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test scenario statistics
    stats = get_scenario_statistics()
    print(f"\n📊 Preset Scenario Statistics:")
    print(f"  - Beginner: {stats['beginner_count']}")
    print(f"  - Intermediate: {stats['intermediate_count']}")
    print(f"  - Advanced: {stats['advanced_count']}")
    print(f"  - Total: {stats['total_preset']}")
    
    levels = ["beginner", "intermediate", "advanced"]
    
    for level in levels:
        print(f"\n\n🎲 Testing {level.upper()} level AI generation...")
        
        try:
            # Test AI generation
            scenario = await get_ai_scenario_by_level(level)
            print_scenario(scenario, f"AI-Generated {level.title()} Scenario")
            
            # Validate scenario structure
            required_fields = ["id", "title", "description", "goal", "context", "product", "hints", "example_good"]
            missing_fields = [field for field in required_fields if field not in scenario]
            
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
            else:
                print("✅ All required fields present")
            
            # Check if it's an AI scenario (id ending with 99 or appropriate prefix)
            expected_prefix = level[0]
            if scenario['id'].startswith(expected_prefix):
                print(f"✅ Correct ID prefix: {scenario['id']}")
            else:
                print(f"⚠️  Unexpected ID format: {scenario['id']}")
                
        except Exception as e:
            print(f"❌ Error generating {level} scenario: {str(e)}")
            print("This might be due to:")
            print("  - Missing environment variables (GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION)")
            print("  - Invalid Vertex AI credentials")
            print("  - Network connectivity issues")
    
    print(f"\n\n🎲 Testing Mixed Mode...")
    try:
        # Test mixed mode with high AI probability
        scenario = await get_mixed_scenario_by_level("intermediate", ai_probability=0.8)
        print_scenario(scenario, "Mixed Mode Scenario (80% AI probability)")
        
        # Test mixed mode with low AI probability  
        scenario = await get_mixed_scenario_by_level("beginner", ai_probability=0.2)
        print_scenario(scenario, "Mixed Mode Scenario (20% AI probability)")
        
    except Exception as e:
        print(f"❌ Error testing mixed mode: {str(e)}")
    
    print(f"\n\n✅ AI Scenario Generation Test Complete!")
    print(f"💡 If you see any errors, check your .env file configuration.")

async def test_scenario_comparison():
    """Compare AI and preset scenarios side by side"""
    print("\n\n🔍 SCENARIO COMPARISON TEST")
    print("="*80)
    
    level = "intermediate"
    
    # Get preset scenario
    generator = CopilotScenarioGenerator()
    preset_scenario = generator.get_random_scenario(level)
    print_scenario(preset_scenario, f"PRESET {level.title()} Scenario")
    
    # Get AI scenario
    try:
        ai_scenario = await generator.get_ai_generated_scenario(level)
        print_scenario(ai_scenario, f"AI-GENERATED {level.title()} Scenario")
        
        print("\n🔍 COMPARISON ANALYSIS:")
        print("-" * 40)
        print(f"Preset ID format: {preset_scenario['id']}")
        print(f"AI ID format: {ai_scenario['id']}")
        print(f"Preset product: {preset_scenario['product']}")
        print(f"AI product: {ai_scenario['product']}")
        print(f"Preset hints count: {len(preset_scenario['hints'])}")
        print(f"AI hints count: {len(ai_scenario['hints'])}")
        
    except Exception as e:
        print(f"❌ Could not generate AI scenario for comparison: {str(e)}")

def test_fallback_scenarios():
    """Test fallback scenarios when AI generation fails"""
    print("\n\n🛟 FALLBACK SCENARIO TEST")
    print("="*50)
    
    # This would normally test what happens when AI generation fails
    # For now, we'll just show the structure of fallback scenarios
    print("Fallback scenarios are created when:")
    print("  - API calls fail")
    print("  - JSON parsing fails")
    print("  - Network issues occur")
    print("\nFallback scenarios use ID format: [level]99 (e.g., 'b99', 'i99', 'a99')")

if __name__ == "__main__":
    print("🚀 Starting AI Scenario Generation Tests...")
    print("Make sure your .env file is configured with:")
    print("  - GOOGLE_CLOUD_PROJECT")
    print("  - GOOGLE_CLOUD_LOCATION") 
    print("  - LLM_MODEL")
    print("  - Valid Vertex AI credentials")
    
    # Run the tests
    asyncio.run(test_ai_generation())
    asyncio.run(test_scenario_comparison())
    test_fallback_scenarios()
    
    print("\n🎯 Test complete! You can now use the AI scenario generation in your Streamlit app.")
    print("💡 Try different generation modes in Practice Mode:")
    print("   📚 Preset Scenarios - Hand-crafted examples")
    print("   🤖 AI-Generated - Fresh scenarios using few-shot prompting")
    print("   🎲 Mixed Mode - Random blend of both")