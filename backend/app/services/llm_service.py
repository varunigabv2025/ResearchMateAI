"""
LLM service with modular API provider support.
"""
import httpx
from typing import List, Dict, Optional

from app.core.config import settings


class LLMService:
    """
    Service for generating responses using configured LLM API provider.
    Supports OpenAI-compatible APIs.
    """
    
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.api_base_url = settings.LLM_API_BASE_URL
        self.timeout = 60.0  # Longer timeout for LLM responses
        self.max_tokens = 1000  # Default max tokens for answer
        self.temperature = 0.3  # Lower temperature for factual answers
    
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
        
        # Prepare API request
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
                answer = data["choices"][0]["message"]["content"]
                
                return answer.strip()
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                raise Exception(f"LLM API error: {e.response.status_code} - {error_detail}")
            except httpx.RequestError as e:
                raise Exception(f"LLM API request failed: {str(e)}")
            except (KeyError, IndexError) as e:
                raise Exception(f"Unexpected LLM API response format: missing {str(e)}")
    
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
