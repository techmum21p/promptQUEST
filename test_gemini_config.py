"""
Simple test script to verify Google AI Studio configuration
Run this first to make sure your API key works before running the main app.
"""

import os
from dotenv import load_dotenv
import google.genai as genai
from google.genai.types import GenerateContentConfig

def test_gemini_config():
    """Test the Gemini API configuration"""
    
    # Load environment variables
    load_dotenv()
    
    print("🧪 Testing Google AI Studio Configuration...")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv('GOOGLE_API_KEY')
    model = os.getenv('LLM_MODEL', 'gemini-2.5-flash')
    use_vertexai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE').upper() == 'TRUE'
    
    print(f"📋 Configuration:")
    print(f"   Model: {model}")
    print(f"   Using Vertex AI: {use_vertexai}")
    print(f"   API Key: {'✅ Set' if api_key else '❌ Missing'}")
    
    if not api_key:
        print("\n❌ Error: GOOGLE_API_KEY not found!")
        print("Please:")
        print("1. Copy env-example.env to .env")
        print("2. Get your API key from https://aistudio.google.com/")
        print("3. Replace 'your-api-key-here' with your actual API key")
        return False
    
    try:
        # Initialize client
        print(f"\n🔧 Initializing client...")
        if use_vertexai:
            project = os.getenv('GOOGLE_CLOUD_PROJECT')
            location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
            client = genai.Client(vertexai=True, project=project, location=location)
            print(f"   Using Vertex AI (project: {project}, location: {location})")
        else:
            client = genai.Client(api_key=api_key)
            print(f"   Using Google AI Studio")
        
        # Test with a simple prompt
        print(f"\n🚀 Sending test message to {model}...")
        
        test_prompt = "Hello! Please respond with 'Gemini API works!' if this is working correctly."
        
        response = client.models.generate_content(
            model=model,
            contents=test_prompt,
            config=GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=100
            )
        )
        
        # Extract response
        response_text = ""
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
        
        print(f"\n✅ Success! Model Response:")
        print(f"   {response_text}")
        print(f"\n🎉 Your app should work correctly now!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"\n🔧 Troubleshooting:")
        print(f"1. Check your API key is correct")
        print(f"2. Make sure you have internet connection")
        print(f"3. Verify the model name '{model}' is supported")
        return False

if __name__ == "__main__":
    test_gemini_config()
