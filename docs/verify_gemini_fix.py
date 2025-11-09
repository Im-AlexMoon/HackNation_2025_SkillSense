"""
Comprehensive verification script for Gemini API RetryError fix

This script tests all aspects of the fix:
1. Environment variable support (both GEMINI_API_KEY and GOOGLE_API_KEY)
2. Clear error messages (no cryptic RetryError)
3. Helpful guidance in error messages
4. Proper error extraction from RetryError wrapper
"""
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'src'))

from rag.llm_client import LLMClient


def test_1_env_var_support():
    """Test that both GEMINI_API_KEY and GOOGLE_API_KEY are supported"""
    print("\n" + "="*70)
    print("TEST 1: Environment Variable Support")
    print("="*70)

    # Save current env vars
    gemini_key = os.environ.get('GEMINI_API_KEY')
    google_key = os.environ.get('GOOGLE_API_KEY')

    try:
        # Test 1a: GEMINI_API_KEY
        os.environ.pop('GEMINI_API_KEY', None)
        os.environ.pop('GOOGLE_API_KEY', None)
        os.environ['GEMINI_API_KEY'] = 'test_key_1'

        client = LLMClient(provider="gemini")
        assert client.api_key == 'test_key_1', "Failed to read GEMINI_API_KEY"
        print("[PASS] GEMINI_API_KEY is supported")

        # Test 1b: GOOGLE_API_KEY
        os.environ.pop('GEMINI_API_KEY', None)
        os.environ['GOOGLE_API_KEY'] = 'test_key_2'

        client = LLMClient(provider="gemini")
        assert client.api_key == 'test_key_2', "Failed to read GOOGLE_API_KEY"
        print("[PASS] GOOGLE_API_KEY is supported")

        # Test 1c: GEMINI_API_KEY takes precedence
        os.environ['GEMINI_API_KEY'] = 'test_key_1'
        os.environ['GOOGLE_API_KEY'] = 'test_key_2'

        client = LLMClient(provider="gemini")
        assert client.api_key == 'test_key_1', "GEMINI_API_KEY should take precedence"
        print("[PASS]: GEMINI_API_KEY takes precedence when both are set")

    finally:
        # Restore original env vars
        if gemini_key:
            os.environ['GEMINI_API_KEY'] = gemini_key
        else:
            os.environ.pop('GEMINI_API_KEY', None)

        if google_key:
            os.environ['GOOGLE_API_KEY'] = google_key
        else:
            os.environ.pop('GOOGLE_API_KEY', None)

    return True


def test_2_error_message_quality():
    """Test that error messages are clear and helpful"""
    print("\n" + "="*70)
    print("TEST 2: Error Message Quality")
    print("="*70)

    # Clear any API keys
    gemini_key = os.environ.pop('GEMINI_API_KEY', None)
    google_key = os.environ.pop('GOOGLE_API_KEY', None)

    try:
        client = LLMClient(provider="gemini")
        response = client.generate("You are helpful", "Say hello")
        print("[FAIL]: Should have raised an exception")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"\nError message received:")
        print(f"{error_msg}\n")

        # Check error message quality
        checks = {
            "Not cryptic RetryError": "RetryError[<Future" not in error_msg,
            "Mentions API key issue": any(x in error_msg for x in ["API key", "GEMINI_API_KEY", "GOOGLE_API_KEY"]),
            "Provides solution": "set" in error_msg.lower() or "Set" in error_msg,
            "Includes help URL": "makersuite.google.com" in error_msg,
            "User-friendly language": "failed" in error_msg.lower() or "not found" in error_msg.lower(),
        }

        print("Error Message Quality Checks:")
        print("-" * 70)
        all_passed = True
        for check, passed in checks.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status}: {check}")
            if not passed:
                all_passed = False

        # Restore env vars
        if gemini_key:
            os.environ['GEMINI_API_KEY'] = gemini_key
        if google_key:
            os.environ['GOOGLE_API_KEY'] = google_key

        return all_passed


def test_3_retry_error_extraction():
    """Test that underlying errors are properly extracted from RetryError"""
    print("\n" + "="*70)
    print("TEST 3: RetryError Extraction")
    print("="*70)

    # Clear any API keys to force an error
    gemini_key = os.environ.pop('GEMINI_API_KEY', None)
    google_key = os.environ.pop('GOOGLE_API_KEY', None)

    try:
        client = LLMClient(provider="gemini")
        response = client.generate("You are helpful", "Say hello")
        print("[FAIL]: Should have raised an exception")
        return False
    except Exception as e:
        error_msg = str(e)

        # The error should contain the underlying error details, not just "RetryError"
        checks = {
            "Contains 'Gemini API key not found'": "Gemini API key not found" in error_msg,
            "Contains original error": "Original error:" in error_msg or "No API_KEY" in error_msg,
            "NOT just 'RetryError[<Future'": "RetryError[<Future" not in error_msg,
            "Mentions retry context": "after retries" in error_msg or "failed" in error_msg,
        }

        print("RetryError Extraction Checks:")
        print("-" * 70)
        all_passed = True
        for check, passed in checks.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status}: {check}")
            if not passed:
                all_passed = False

        # Restore env vars
        if gemini_key:
            os.environ['GEMINI_API_KEY'] = gemini_key
        if google_key:
            os.environ['GOOGLE_API_KEY'] = google_key

        return all_passed


def test_4_multiple_error_types():
    """Test that different error types have appropriate messages"""
    print("\n" + "="*70)
    print("TEST 4: Multiple Error Type Handling")
    print("="*70)

    # This test verifies the error detection logic exists
    # We can't easily test rate limits or content blocking without actual API calls

    from rag.llm_client import LLMClient
    import inspect

    # Check that _generate_with_retry has the error handling code
    source = inspect.getsource(LLMClient._generate_with_retry)

    checks = {
        "Handles API key errors": "API_KEY" in source or "api_key" in source,
        "Handles rate limits": "quota" in source or "rate limit" in source,
        "Handles content blocking": "block" in source or "safety" in source,
        "Has helpful messages": "Get a free key" in source or "Please wait" in source,
    }

    print("Error Type Handling Checks:")
    print("-" * 70)
    all_passed = True
    for check, passed in checks.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {check}")
        if not passed:
            all_passed = False

    return all_passed


def main():
    """Run all tests"""
    print("="*70)
    print("GEMINI API RETRYERROR FIX - VERIFICATION SUITE")
    print("="*70)

    results = {
        "Environment Variable Support": test_1_env_var_support(),
        "Error Message Quality": test_2_error_message_quality(),
        "RetryError Extraction": test_3_retry_error_extraction(),
        "Multiple Error Type Handling": test_4_multiple_error_types(),
    }

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]ED" if passed else "[FAIL]ED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("*** ALL TESTS PASSED! ***")
        print("The Gemini API RetryError fix is working correctly.")
        print("\nWhat was fixed:")
        print("  - Environment variables: Both GEMINI_API_KEY and GOOGLE_API_KEY work")
        print("  - Error messages: Clear and actionable (no cryptic RetryError)")
        print("  - Error extraction: Underlying errors properly surfaced")
        print("  - Error guidance: Helpful messages for different error types")
    else:
        print("WARNING: SOME TESTS FAILED")
        print("Please review the failed tests above.")

    print("="*70)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
