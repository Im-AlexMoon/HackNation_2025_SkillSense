"""
Debug script to investigate Gemini API RetryError
This script will help identify the actual exception beneath the RetryError
"""
import sys
from pathlib import Path
import traceback

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from rag.llm_client import LLMClient

def test_gemini_with_detailed_error():
    """Test Gemini API and capture detailed error information"""
    print("=" * 60)
    print("Testing Gemini API - Detailed Error Investigation")
    print("=" * 60)

    try:
        # Initialize client
        print("\n1. Initializing Gemini client...")
        client = LLMClient(provider="gemini")

        print(f"   Provider: {client.provider}")
        print(f"   Model: {client.model}")
        print(f"   Has API Key: {client.api_key is not None}")

        # Try to generate content
        print("\n2. Attempting to generate content...")
        system_prompt = "You are a helpful assistant."
        user_prompt = "Say hello."

        response = client.generate(system_prompt, user_prompt)

        print("\n✅ SUCCESS!")
        print(f"Response: {response}")

    except Exception as e:
        print("\n❌ ERROR OCCURRED!")
        print("=" * 60)

        # Get exception details
        print(f"\nException Type: {type(e).__name__}")
        print(f"Exception Message: {str(e)}")

        # Print full traceback
        print("\nFull Traceback:")
        print("-" * 60)
        traceback.print_exc()

        # Try to get the underlying exception from tenacity RetryError
        print("\n" + "=" * 60)
        print("Attempting to extract underlying exception...")
        print("=" * 60)

        if hasattr(e, 'last_attempt'):
            print("\n✓ Found 'last_attempt' attribute")
            last_attempt = e.last_attempt

            if hasattr(last_attempt, 'exception'):
                print("✓ Found 'exception' method")
                try:
                    underlying_exception = last_attempt.exception()
                    print(f"\nUnderlying Exception Type: {type(underlying_exception).__name__}")
                    print(f"Underlying Exception Message: {str(underlying_exception)}")

                    print("\nUnderlying Exception Traceback:")
                    print("-" * 60)
                    import traceback
                    traceback.print_exception(type(underlying_exception), underlying_exception, underlying_exception.__traceback__)

                except Exception as extract_error:
                    print(f"❌ Error extracting exception: {extract_error}")

            if hasattr(last_attempt, 'result'):
                print("✓ Found 'result' method")
                try:
                    result = last_attempt.result()
                    print(f"Result: {result}")
                except Exception as result_error:
                    print(f"Result Error: {result_error}")

        # Check for common Gemini issues
        print("\n" + "=" * 60)
        print("Common Gemini API Issues Checklist:")
        print("=" * 60)

        error_str = str(e).lower()

        if "api" in error_str and "key" in error_str:
            print("\n🔑 API KEY ISSUE DETECTED")
            print("   - Check if GEMINI_API_KEY is set in .env")
            print("   - Verify the API key is valid")
            print("   - Get a key at: https://makersuite.google.com/app/apikey")

        if "quota" in error_str or "rate" in error_str or "limit" in error_str:
            print("\n⏱️ RATE LIMIT ISSUE DETECTED")
            print("   - You may have exceeded the free tier quota")
            print("   - Wait a few minutes and try again")

        if "block" in error_str or "safety" in error_str:
            print("\n🚫 CONTENT BLOCKED DETECTED")
            print("   - Content may have been flagged by safety filters")
            print("   - Try modifying the prompt")

        if "network" in error_str or "connection" in error_str:
            print("\n🌐 NETWORK ISSUE DETECTED")
            print("   - Check your internet connection")
            print("   - Check if Google APIs are accessible")

if __name__ == "__main__":
    test_gemini_with_detailed_error()
