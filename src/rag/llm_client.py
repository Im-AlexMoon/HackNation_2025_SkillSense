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
        return response.choices[0].message.content

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
        return response.content[0].text

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

        print("\n✓ LLM Client module loaded successfully")
    except Exception as e:
        print(f"\n⚠️  Note: {str(e)}")
        print("To test, set GEMINI_API_KEY environment variable")
        print("LLM Client module loaded (no API key configured)")
