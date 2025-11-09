"""
Multi-Provider LLM Client
Unified interface for OpenAI, Anthropic, and Google Gemini
"""
import os
from typing import Optional, List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError


class LLMClient:
    """Unified LLM client supporting multiple providers"""

    SUPPORTED_PROVIDERS = ["gemini", "openai", "anthropic"]

    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM client

        Args:
            provider: LLM provider ("gemini", "openai", or "anthropic")
            api_key: API key (if None, loads from environment)
            model: Specific model to use (if None, uses default for provider)
        """
        self.provider = provider.lower()

        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Provider must be one of {self.SUPPORTED_PROVIDERS}")

        # Get API key
        self.api_key = api_key or self._get_api_key_from_env()

        # Initialize client
        self.client = None
        self.model = model
        self._initialize_client()

    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variables"""
        env_vars = {
            "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],  # Support both env var names
            "openai": ["OPENAI_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY"]
        }

        env_var_names = env_vars.get(self.provider, [])
        # Try each possible environment variable name
        for env_var in env_var_names:
            api_key = os.getenv(env_var)
            if api_key:
                return api_key
        return None

    def _initialize_client(self):
        """Initialize provider-specific client"""
        if self.provider == "openai":
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            self.model = self.model or "gpt-4o-mini"

        elif self.provider == "gemini":
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
            else:
                print("WARNING: No Gemini API key provided. Requests may fail or have limited quota.")
                print("Get a free key at: https://makersuite.google.com/app/apikey")
            self.model = self.model or "gemini-2.0-flash-exp"
            self.client = genai.GenerativeModel(self.model)

        elif self.provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = self.model or "claude-3-5-haiku-20241022"

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """
        Generate response from LLM with improved error handling

        Args:
            system_prompt: System/instruction prompt
            user_prompt: User query/prompt
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Generated text response
        """
        try:
            return self._generate_with_retry(system_prompt, user_prompt, temperature)
        except RetryError as e:
            # Extract the actual underlying exception from RetryError
            underlying_error = self._extract_underlying_error(e)
            raise Exception(f"LLM generation failed after retries ({self.provider}): {underlying_error}")
        except Exception as e:
            # Re-raise other exceptions with context
            raise Exception(f"LLM generation failed ({self.provider}): {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _generate_with_retry(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Internal method with retry logic"""
        try:
            if self.provider == "openai":
                return self._call_openai(system_prompt, user_prompt, temperature)
            elif self.provider == "gemini":
                return self._call_gemini(system_prompt, user_prompt, temperature)
            elif self.provider == "anthropic":
                return self._call_anthropic(system_prompt, user_prompt, temperature)
        except Exception as e:
            # Add helpful context to the exception
            error_msg = str(e)

            # Provide helpful guidance based on error type
            if "DefaultCredentialsError" in str(type(e)) or "API_KEY" in error_msg or "api_key" in error_msg.lower():
                if self.provider == "gemini":
                    raise Exception(
                        f"Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.\n"
                        f"Get a free key at: https://makersuite.google.com/app/apikey\n"
                        f"Original error: {error_msg}"
                    )
                else:
                    raise Exception(
                        f"API key error for {self.provider}. Please check your API key configuration.\n"
                        f"Original error: {error_msg}"
                    )
            elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise Exception(
                    f"Rate limit or quota exceeded for {self.provider}.\n"
                    f"Please wait a few minutes or upgrade your API plan.\n"
                    f"Original error: {error_msg}"
                )
            elif "block" in error_msg.lower() or "safety" in error_msg.lower():
                raise Exception(
                    f"Content was blocked by {self.provider} safety filters.\n"
                    f"Try modifying your prompt.\n"
                    f"Original error: {error_msg}"
                )
            else:
                # Re-raise with original message
                raise

    def _extract_underlying_error(self, retry_error: RetryError) -> str:
        """Extract the actual error message from a RetryError"""
        try:
            if hasattr(retry_error, 'last_attempt'):
                last_attempt = retry_error.last_attempt
                if hasattr(last_attempt, 'exception') and callable(last_attempt.exception):
                    underlying_exception = last_attempt.exception()
                    if underlying_exception:
                        return str(underlying_exception)
        except Exception:
            pass

        # Fallback to the retry error's string representation
        return str(retry_error)

    def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=1024
        )

        # Validate response structure
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise ValueError("Invalid OpenAI response: No choices returned")

        message_content = response.choices[0].message.content
        if message_content is None or not isinstance(message_content, str):
            raise ValueError("Invalid OpenAI response: Empty or invalid message content")

        return message_content

    def _call_gemini(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call Google Gemini API"""
        # Gemini doesn't have separate system prompt, so combine them
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": 1024,
        }

        response = self.client.generate_content(
            combined_prompt,
            generation_config=generation_config
        )

        # Validate response
        if not response:
            raise ValueError("Invalid Gemini response: No response returned")

        # Check if content was blocked
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            block_reason = getattr(response.prompt_feedback, 'block_reason', None)
            if block_reason:
                raise ValueError(f"Gemini blocked the request: {block_reason}")

        # Validate text content
        if not hasattr(response, 'text') or not response.text:
            # Check for candidates with finish_reason
            if hasattr(response, 'candidates') and response.candidates:
                finish_reason = getattr(response.candidates[0], 'finish_reason', 'UNKNOWN')
                raise ValueError(f"Gemini returned no text. Finish reason: {finish_reason}")
            raise ValueError("Invalid Gemini response: No text content returned")

        return response.text

    def _call_anthropic(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call Anthropic Claude API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # Validate response structure
        if not response:
            raise ValueError("Invalid Anthropic response: No response returned")

        if not hasattr(response, 'content') or not response.content:
            raise ValueError("Invalid Anthropic response: No content blocks returned")

        # Check stop reason
        if hasattr(response, 'stop_reason') and response.stop_reason not in ['end_turn', None]:
            raise ValueError(f"Anthropic stopped unexpectedly: {response.stop_reason}")

        text_content = response.content[0].text
        if not text_content or not isinstance(text_content, str):
            raise ValueError("Invalid Anthropic response: Empty or invalid text content")

        return text_content

    def get_provider_info(self) -> Dict[str, str]:
        """Get information about current provider"""
        return {
            "provider": self.provider,
            "model": self.model,
            "has_api_key": self.api_key is not None
        }


# Example usage
if __name__ == "__main__":
    # Test with Gemini (free tier)
    print("Testing LLM Client with Gemini...")

    try:
        client = LLMClient(provider="gemini")

        system_prompt = "You are a helpful assistant analyzing candidate profiles."
        user_prompt = "Does a candidate with Python and React skills fit a Full Stack Developer role?"

        response = client.generate(system_prompt, user_prompt)
        print(f"\nResponse: {response[:200]}...")

        print("\nLLM Client module loaded successfully")
    except Exception as e:
        print(f"\nNote: {str(e)}")
        print("To test, set GEMINI_API_KEY environment variable")
        print("LLM Client module loaded (no API key configured)")
