"""
LLM service with modular API provider support.
"""
import httpx
from typing import List, Dict, Optional
from enum import Enum

from app.core.config import settings


class LLMProvider(str, Enum):
    """Supported LLM API providers."""
    OPENAI_COMPATIBLE = "openai"  # OpenRouter, OpenAI, etc.
    GEMINI_NATIVE = "gemini"      # Google Gemini API (Gemma, Gemini models)


class LLMService:
    """
    Service for generating responses using configured LLM API provider.
    Supports OpenAI-compatible APIs and Google Gemini API.
    """

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.api_base_url = settings.LLM_API_BASE_URL
        self.provider = self._detect_provider()
        self.timeout = 60.0  # Longer timeout for LLM responses
        self.max_tokens = 1000  # Default max tokens for answer
        self.temperature = 0.3  # Lower temperature for factual answers

    def _detect_provider(self) -> LLMProvider:
        """
        Detect the API provider based on base URL or explicit configuration.
        """
        # Check for explicit provider configuration via settings attribute
        # Use getattr to handle both real settings and mocked settings
        provider_str = ''
        if hasattr(settings, 'LLM_PROVIDER'):
            provider_str = str(getattr(settings, 'LLM_PROVIDER', '')).lower()

        # Explicit provider configuration takes precedence
        if provider_str == 'gemini':
            return LLMProvider.GEMINI_NATIVE
        elif provider_str == 'openai':
            return LLMProvider.OPENAI_COMPATIBLE

        # Auto-detect based on base URL
        if 'generativelanguage.googleapis.com' in self.api_base_url:
            return LLMProvider.GEMINI_NATIVE

        # Default to OpenAI-compatible
        return LLMProvider.OPENAI_COMPATIBLE

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a chat completion using the configured LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens in response (overrides default)

        Returns:
            Generated text response

        Raises:
            Exception: If LLM API call fails
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")

        # Route to appropriate provider implementation
        if self.provider == LLMProvider.GEMINI_NATIVE:
            return await self._generate_gemini_native(messages, temperature, max_tokens)
        else:
            return await self._generate_openai_compatible(messages, temperature, max_tokens)

    async def _generate_openai_compatible(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate completion using OpenAI-compatible API format.
        """
        url = f"{self.api_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()

                # Extract the assistant's response
                message = data["choices"][0]["message"]
                answer = message.get("content")

                if not answer or not isinstance(answer, str) or not answer.strip():
                    raise Exception("LLM provider returned empty response content")

                return answer.strip()

            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                raise Exception(f"LLM API error: {e.response.status_code} - {error_detail}")
            except httpx.RequestError as e:
                raise Exception(f"LLM API request failed: {str(e)}")
            except (KeyError, IndexError) as e:
                raise Exception(f"Unexpected LLM API response format: missing {str(e)}")

    async def _generate_gemini_native(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate completion using Google Gemini API native format.
        Supports Gemma and Gemini models hosted on Gemini API.
        """
        # Build Gemini API URL with API key as query parameter
        url = f"{self.api_base_url.rstrip('/')}/models/{self.model}:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        # Separate system instruction from user messages
        system_instruction = None
        user_contents = []

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                user_contents.append({"parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                # Gemini API format uses "model" role for assistant responses
                user_contents.append({
                    "role": "model",
                    "parts": [{"text": msg["content"]}]
                })

        # Build payload in Gemini API format
        payload = {
            "contents": user_contents
        }

        # Add system instruction if present
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Add generation config
        generation_config = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        elif self.temperature is not None:
            generation_config["temperature"] = self.temperature

        if max_tokens is not None:
            generation_config["maxOutputTokens"] = max_tokens
        elif self.max_tokens is not None:
            generation_config["maxOutputTokens"] = self.max_tokens

        if generation_config:
            payload["generationConfig"] = generation_config

        # Add API key as query parameter
        params = {"key": self.api_key}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()

                # Extract text from Gemini API response format
                # Response structure: {candidates: [{content: {parts: [{text: "..."}]}}]}
                # Note: Some models return multiple parts, including "thought" parts
                try:
                    candidate = data["candidates"][0]
                    content = candidate["content"]
                    parts = content["parts"]

                    # Collect all non-thought text parts
                    text_parts = []
                    for part in parts:
                        if "text" in part:
                            # Skip thought parts if flagged
                            if part.get("thought", False):
                                continue
                            text_parts.append(part["text"])

                    # If no non-thought parts, use the last text part
                    if not text_parts and parts:
                        for part in reversed(parts):
                            if "text" in part:
                                text_parts.append(part["text"])
                                break

                    answer = "\n".join(text_parts) if text_parts else ""

                except (KeyError, IndexError, TypeError) as e:
                    raise Exception(f"Unexpected Gemini API response structure: {str(e)}")

                if not answer or not isinstance(answer, str) or not answer.strip():
                    raise Exception("Gemini API returned empty response content")

                return answer.strip()

            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                # Handle Gemini API specific errors (e.g., 429 for rate limits)
                status_code = e.response.status_code
                if status_code == 429:
                    raise Exception(f"Gemini API rate limit exceeded: {error_detail}")
                raise Exception(f"Gemini API error: {status_code} - {error_detail}")
            except httpx.RequestError as e:
                raise Exception(f"Gemini API request failed: {str(e)}")
            except Exception as e:
                # Re-raise exceptions we've already formatted
                if "Gemini API" in str(e) or "response" in str(e).lower():
                    raise
                raise Exception(f"Unexpected Gemini API error: {str(e)}")

    async def generate_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate an answer using system and user prompts.
        Convenience wrapper around generate_chat_completion.

        Args:
            system_prompt: System instruction
            user_prompt: User's prompt/question
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return await self.generate_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def generate_chat_completion_sync(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Synchronous wrapper for generate_chat_completion.
        Useful for non-async contexts.
        """
        import asyncio
        return asyncio.run(
            self.generate_chat_completion(messages, temperature, max_tokens)
        )

    def generate_answer_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Synchronous wrapper for generate_answer.
        Useful for non-async contexts.
        """
        import asyncio
        return asyncio.run(
            self.generate_answer(system_prompt, user_prompt, temperature, max_tokens)
        )


# Global instance
llm_service = LLMService()
