"""
Multi-Provider LLM Client
Unified interface for OpenAI, Anthropic, and Google Gemini
"""
import os
from typing import Optional, List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential


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
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }

        env_var = env_vars.get(self.provider)
        if env_var:
            return os.getenv(env_var)
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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """
        Generate response from LLM

        Args:
            system_prompt: System/instruction prompt
            user_prompt: User query/prompt
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Generated text response
        """
        try:
            if self.provider == "openai":
                return self._call_openai(system_prompt, user_prompt, temperature)
            elif self.provider == "gemini":
                return self._call_gemini(system_prompt, user_prompt, temperature)
            elif self.provider == "anthropic":
                return self._call_anthropic(system_prompt, user_prompt, temperature)
        except Exception as e:
            raise Exception(f"LLM generation failed ({self.provider}): {str(e)}")

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
