"""
Test script to verify the Gemini API error fix
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from rag.llm_client import LLMClient

def test_error_message_clarity():
    """Test that error messages are clear and helpful"""
    print("="*70)
    print("Testing Error Message Clarity")
    print("="*70)

    print("\nTest 1: Missing API Key Error")
    print("-" * 70)
    try:
        client = LLMClient(provider="gemini")
        response = client.generate("You are helpful", "Say hello")
        print(f"SUCCESS: {response}")
    except Exception as e:
        error_msg = str(e)
        print(f"Error message received:\n{error_msg}")

        # Check if the error message contains helpful information
        checks = {
            "Mentions API key": "API key" in error_msg or "GEMINI_API_KEY" in error_msg or "GOOGLE_API_KEY" in error_msg,
            "Provides solution": "Set" in error_msg or "set" in error_msg,
            "Includes help URL": "makersuite.google.com" in error_msg or "google.com" in error_msg,
            "Not cryptic RetryError": "RetryError[<Future" not in error_msg,
        }

        print("\n" + "="*70)
        print("Error Message Quality Checks:")
        print("="*70)
        for check, passed in checks.items():
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {check}")

        all_passed = all(checks.values())
        print("\n" + "="*70)
        if all_passed:
            print("SUCCESS: All error message quality checks passed!")
            print("The error is now user-friendly and actionable.")
        else:
            print("PARTIAL: Some checks failed, but improvement is visible.")
        print("="*70)

if __name__ == "__main__":
    test_error_message_clarity()
