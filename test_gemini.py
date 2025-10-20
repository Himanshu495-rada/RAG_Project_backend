"""
Quick test script to verify Google Gemini API setup.
Run this from the backend directory: python test_gemini.py
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini():
    """Test Gemini API connection."""
    print("=" * 60)
    print("Testing Google Gemini API Setup")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✓ GEMINI_API_KEY found: {api_key[:10]}...")
    
    # Try importing the library
    try:
        import google.generativeai as genai
        print("✓ google-generativeai library imported successfully")
    except ImportError as e:
        print(f"❌ ERROR: Could not import google.generativeai: {e}")
        print("   Run: pip install google-generativeai")
        return False
    
    # Configure and test
    try:
        genai.configure(api_key=api_key)
        print("✓ Gemini API configured successfully")
        
        # Create a model instance
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✓ GenerativeModel created: gemini-2.5-flash")
        
        # Test with a simple prompt
        print("\nSending test prompt...")
        response = model.generate_content("Say hello and confirm you're working!")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Gemini Response:")
        print("=" * 60)
        print(response.text)
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini()
    if success:
        print("\n✅ Gemini setup is working correctly!")
        print("   You can now start the Django server and use RAG queries.")
    else:
        print("\n❌ Gemini setup failed. Please check the errors above.")
