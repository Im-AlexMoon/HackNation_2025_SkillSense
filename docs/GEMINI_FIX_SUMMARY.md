# Gemini API RetryError Fix - Summary

## Problem Identified

The SkillSense RAG system was showing a cryptic error when the Gemini API failed:
```
RetryError[<Future at 0x20972864690 state=finished raised Exception>]
```

This error provided no useful information to users about what went wrong or how to fix it.

## Root Causes Discovered

### 1. Environment Variable Name Mismatch
- **Issue**: The code was looking for `GEMINI_API_KEY` in environment variables
- **Problem**: Google's Gemini SDK actually expects `GOOGLE_API_KEY`
- **Result**: Even when users set `GEMINI_API_KEY`, the SDK couldn't find it

### 2. RetryError Masking Underlying Exception
- **Issue**: The `@retry` decorator from `tenacity` was catching exceptions and wrapping them in a `RetryError`
- **Problem**: The actual error message (DefaultCredentialsError) was hidden inside the RetryError
- **Result**: Users only saw "RetryError[<Future...>]" instead of the real problem

### 3. Poor Error Context
- **Issue**: When exceptions were raised, they lacked helpful context
- **Problem**: No guidance on how to fix the issue (where to get API keys, what env vars to set, etc.)
- **Result**: Users were stuck without actionable information

## Actual Underlying Error

The real error beneath the RetryError was:
```
google.auth.exceptions.DefaultCredentialsError:
  No API_KEY or ADC found. Please either:
    - Set the `GOOGLE_API_KEY` environment variable.
    - Manually pass the key with `genai.configure(api_key=my_api_key)`.
    - Or set up Application Default Credentials
```

## Solutions Implemented

### Fix 1: Support Both Environment Variable Names

**File**: `src/rag/llm_client.py` - `_get_api_key_from_env()` method

**Before**:
```python
def _get_api_key_from_env(self) -> Optional[str]:
    env_vars = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY"
    }
    env_var = env_vars.get(self.provider)
    if env_var:
        return os.getenv(env_var)
    return None
```

**After**:
```python
def _get_api_key_from_env(self) -> Optional[str]:
    env_vars = {
        "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],  # Support both
        "openai": ["OPENAI_API_KEY"],
        "anthropic": ["ANTHROPIC_API_KEY"]
    }
    env_var_names = env_vars.get(self.provider, [])
    for env_var in env_var_names:
        api_key = os.getenv(env_var)
        if api_key:
            return api_key
    return None
```

**Impact**: Now works with either `GEMINI_API_KEY` or `GOOGLE_API_KEY`

### Fix 2: Extract and Surface Underlying Errors

**File**: `src/rag/llm_client.py` - Restructured `generate()` method

**Changes**:
1. Split the retry logic into a separate `_generate_with_retry()` method
2. Added `_extract_underlying_error()` to extract real errors from RetryError
3. Added specific error handling for common issues (API keys, rate limits, content blocking)

**Before**:
```python
@retry(...)
def generate(self, system_prompt, user_prompt, temperature):
    try:
        # call provider...
    except Exception as e:
        raise Exception(f"LLM generation failed ({self.provider}): {str(e)}")
```

**After**:
```python
def generate(self, system_prompt, user_prompt, temperature):
    try:
        return self._generate_with_retry(system_prompt, user_prompt, temperature)
    except RetryError as e:
        underlying_error = self._extract_underlying_error(e)
        raise Exception(f"LLM generation failed after retries ({self.provider}): {underlying_error}")
    except Exception as e:
        raise Exception(f"LLM generation failed ({self.provider}): {str(e)}")

@retry(...)
def _generate_with_retry(self, system_prompt, user_prompt, temperature):
    try:
        # call provider...
    except Exception as e:
        # Detect error type and provide helpful guidance
        if "API_KEY" in str(e) or "DefaultCredentialsError" in str(type(e)):
            if self.provider == "gemini":
                raise Exception(
                    f"Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY.\n"
                    f"Get a free key at: https://makersuite.google.com/app/apikey\n"
                    f"Original error: {str(e)}"
                )
        # ... other error types
        else:
            raise

def _extract_underlying_error(self, retry_error):
    try:
        if hasattr(retry_error, 'last_attempt'):
            last_attempt = retry_error.last_attempt
            if hasattr(last_attempt, 'exception'):
                return str(last_attempt.exception())
    except Exception:
        pass
    return str(retry_error)
```

**Impact**: Users now see clear, actionable error messages

### Fix 3: Updated Documentation

**File**: `.env.example`

Added documentation for both environment variable names:
```bash
# Google Gemini (Free Tier - Recommended for demos)
# Get key at: https://makersuite.google.com/app/apikey
# You can use either GEMINI_API_KEY or GOOGLE_API_KEY
GEMINI_API_KEY=your_gemini_key_here
# GOOGLE_API_KEY=your_gemini_key_here  # Alternative name
```

## Error Messages Comparison

### Before Fix:
```
RetryError[<Future at 0x20972864690 state=finished raised Exception>]
```

### After Fix:
```
LLM generation failed after retries (gemini): Gemini API key not found.
Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.
Get a free key at: https://makersuite.google.com/app/apikey

Original error:
  No API_KEY or ADC found. Please either:
    - Set the `GOOGLE_API_KEY` environment variable.
    - Manually pass the key with `genai.configure(api_key=my_api_key)`.
    - Or set up Application Default Credentials
```

## Testing the Fix

### Test 1: Error Message Quality
Run: `uv run python test_error_fix.py`

This verifies that error messages:
- ✅ Mention the API key issue
- ✅ Provide solution steps
- ✅ Include helpful URLs
- ✅ Don't show cryptic RetryError

### Test 2: Manual Testing with API Key

1. **Set up environment variable**:
   ```bash
   # Option 1: Use GEMINI_API_KEY
   export GEMINI_API_KEY="your-api-key-here"

   # Option 2: Use GOOGLE_API_KEY (also works now)
   export GOOGLE_API_KEY="your-api-key-here"
   ```

2. **Run the app**:
   ```bash
   uv run streamlit run app.py
   ```

3. **Test the Employer Q&A feature**:
   - Navigate to the "💬 Employer Q&A" page
   - Select "gemini" as the LLM provider
   - Ask a question
   - Should now work or show a clear error message

### Test 3: Integration Test
Create a test profile and use the RAG system:
```python
from rag.llm_client import LLMClient

# Test without API key (should show clear error)
client = LLMClient(provider="gemini")
try:
    response = client.generate("You are helpful", "Hello")
except Exception as e:
    print(f"Clear error: {e}")

# Test with API key
client = LLMClient(provider="gemini", api_key="your-key")
response = client.generate("You are helpful", "Hello")
print(f"Success: {response}")
```

## Common Error Scenarios Now Handled

### 1. Missing API Key
**Error Message**:
```
Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.
Get a free key at: https://makersuite.google.com/app/apikey
```

**Solution**: Set the environment variable in `.env` file

### 2. Rate Limit Exceeded
**Error Message**:
```
Rate limit or quota exceeded for gemini.
Please wait a few minutes or upgrade your API plan.
```

**Solution**: Wait or upgrade API quota

### 3. Content Blocked
**Error Message**:
```
Content was blocked by gemini safety filters.
Try modifying your prompt.
```

**Solution**: Rephrase the prompt to avoid triggering safety filters

## Files Modified

1. **`src/rag/llm_client.py`**
   - Added support for both `GEMINI_API_KEY` and `GOOGLE_API_KEY`
   - Improved error extraction from RetryError
   - Added contextual error messages with solutions

2. **`.env.example`**
   - Documented both environment variable options
   - Added clarifying comments

3. **Test files created**:
   - `debug_gemini_error.py` - Detailed error investigation
   - `test_error_fix.py` - Error message quality verification

## How to Verify the Fix

1. **Check the error message is clear**:
   ```bash
   # Without API key set
   uv run python test_error_fix.py
   # Should show: "SUCCESS: All error message quality checks passed!"
   ```

2. **Test with a valid API key**:
   ```bash
   # Set your API key (get one at https://makersuite.google.com/app/apikey)
   export GEMINI_API_KEY="your-actual-key"

   # Run the test
   uv run python -c "from src.rag.llm_client import LLMClient; c=LLMClient('gemini'); print(c.generate('Be helpful', 'Say hi'))"
   ```

3. **Test in the Streamlit app**:
   ```bash
   uv run streamlit run app.py
   ```
   - Go to Employer Q&A page
   - Try asking questions with and without API key
   - Error messages should be clear and actionable

## Summary

✅ **Fixed**: Environment variable name mismatch (now supports both GEMINI_API_KEY and GOOGLE_API_KEY)
✅ **Fixed**: Cryptic RetryError - now shows actual error message
✅ **Fixed**: Added helpful context and solutions to all error messages
✅ **Improved**: User experience with actionable error information

The error is no longer a mystery - users now get clear guidance on exactly what went wrong and how to fix it!
