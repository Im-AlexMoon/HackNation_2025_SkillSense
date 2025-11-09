# Troubleshooting Guide - SkillSense RAG System

## Common Issues and Solutions

### Issue 1: "Gemini API key not found" Error

**Full Error Message**:
```
LLM generation failed after retries (gemini): Gemini API key not found.
Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.
Get a free key at: https://makersuite.google.com/app/apikey
```

**Cause**: The Gemini API requires an API key, but none was found in your environment.

**Solution**:

1. **Get a free Gemini API key**:
   - Visit https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the key

2. **Set the environment variable**:

   **Option A: Using .env file (Recommended)**
   ```bash
   # Edit the .env file in the project root
   # Add one of these lines:
   GEMINI_API_KEY=your-api-key-here
   # OR
   GOOGLE_API_KEY=your-api-key-here
   ```

   **Option B: Command line (Temporary)**
   ```bash
   # Windows (Command Prompt)
   set GEMINI_API_KEY=your-api-key-here

   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your-api-key-here"

   # Linux/Mac
   export GEMINI_API_KEY="your-api-key-here"
   ```

3. **Restart the application**:
   ```bash
   uv run streamlit run app.py
   ```

---

### Issue 2: "Rate limit or quota exceeded" Error

**Full Error Message**:
```
Rate limit or quota exceeded for gemini.
Please wait a few minutes or upgrade your API plan.
```

**Cause**: You've hit the rate limit for the Gemini free tier (15 requests per minute).

**Solutions**:

1. **Wait a few minutes** and try again
2. **Reduce request frequency** - space out your queries
3. **Upgrade to a paid plan** if you need higher limits
4. **Switch to a different provider** temporarily (OpenAI or Anthropic)

---

### Issue 3: "Content was blocked" Error

**Full Error Message**:
```
Content was blocked by gemini safety filters.
Try modifying your prompt.
```

**Cause**: Gemini's safety filters flagged your content.

**Solutions**:

1. **Rephrase your question** to be more neutral
2. **Avoid sensitive topics** (politics, violence, etc.)
3. **Try a different provider** (OpenAI or Anthropic may have different filters)

---

### Issue 4: Cannot Connect to Gemini API

**Symptoms**:
- Timeout errors
- Network connection errors
- DNS resolution failures

**Solutions**:

1. **Check internet connection**:
   ```bash
   ping google.com
   ```

2. **Check firewall/proxy settings**:
   - Ensure your firewall allows HTTPS connections
   - If behind a corporate firewall, you may need to configure proxy settings

3. **Verify Google API access**:
   ```bash
   curl https://generativelanguage.googleapis.com
   ```

---

### Issue 5: Wrong Environment Variable Name

**Symptom**: You set `GEMINI_API_KEY` but still get "API key not found" error.

**Cause**: Older versions only supported `GEMINI_API_KEY`, but Google's SDK prefers `GOOGLE_API_KEY`.

**Solution**: The current version supports BOTH names. Try both:
```bash
# .env file - try both
GEMINI_API_KEY=your-key
GOOGLE_API_KEY=your-key
```

---

## Switching LLM Providers

If Gemini isn't working, you can switch to alternative providers:

### OpenAI (GPT-4o-mini)

1. Get API key: https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   OPENAI_API_KEY=your-openai-key
   ```
3. In Streamlit app, select "openai" as the LLM provider

### Anthropic (Claude)

1. Get API key: https://console.anthropic.com/
2. Set environment variable:
   ```bash
   ANTHROPIC_API_KEY=your-anthropic-key
   ```
3. In Streamlit app, select "anthropic" as the LLM provider

---

## Testing Your Setup

### Quick Test Script

Create a file `test_llm.py`:
```python
import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / 'src'))

from rag.llm_client import LLMClient

# Test Gemini
print("Testing Gemini API...")
try:
    client = LLMClient(provider="gemini")
    response = client.generate(
        "You are a helpful assistant.",
        "Say hello in one sentence."
    )
    print(f"✅ SUCCESS: {response}")
except Exception as e:
    print(f"❌ ERROR: {e}")
```

Run it:
```bash
uv run python test_llm.py
```

### Expected Results

**With valid API key**:
```
Testing Gemini API...
✅ SUCCESS: Hello! How can I help you today?
```

**Without API key**:
```
Testing Gemini API...
❌ ERROR: LLM generation failed after retries (gemini): Gemini API key not found.
Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.
Get a free key at: https://makersuite.google.com/app/apikey
```

---

## Debugging Tips

### Enable Verbose Logging

Add this to your code to see more details:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Environment Variables

```python
import os
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY', 'Not set')}")
print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY', 'Not set')}")
```

### Verify .env File is Loaded

The app uses `python-dotenv` to load `.env` files. Make sure:
1. `.env` file exists in project root
2. File has correct format (KEY=value, no spaces around =)
3. No quotes needed around values

---

## Still Having Issues?

1. **Check the error message carefully** - it now includes specific guidance
2. **Try the test script above** to isolate the issue
3. **Verify your API key is valid** by testing it at the provider's website
4. **Check for typos** in environment variable names
5. **Restart the application** after changing environment variables

---

## API Key Best Practices

1. **Never commit API keys to git** - they're in `.gitignore`
2. **Use .env file** for local development
3. **Rotate keys regularly** for security
4. **Use different keys** for dev/staging/production
5. **Monitor usage** on provider dashboards to avoid surprise charges

---

## Quick Reference: Error Message Meanings

| Error Contains | Means | Solution |
|----------------|-------|----------|
| "API key not found" | Missing API key | Set GEMINI_API_KEY or GOOGLE_API_KEY |
| "Rate limit" | Too many requests | Wait or upgrade plan |
| "Quota exceeded" | Hit usage limit | Wait or upgrade plan |
| "Content blocked" | Safety filter triggered | Rephrase prompt |
| "Network" / "Connection" | Can't reach API | Check internet/firewall |
| "Invalid API key" | Key is wrong | Check key, regenerate if needed |
| "Permission denied" | Key lacks permissions | Check API key settings |

---

## Version Information

This troubleshooting guide applies to SkillSense with the improved error handling (November 2025+).

If you're seeing cryptic errors like `RetryError[<Future at 0x...>]`, you may have an older version.
Update to the latest code to get clear, actionable error messages.
