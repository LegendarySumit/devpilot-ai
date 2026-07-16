"""
Unified LLM Provider - Handles all LLM APIs
Supports Gemini, Groq, Mistral, OpenRouter, Cerebras
Users can choose any model from any provider
"""
import requests
import time
from typing import Dict, Any, Optional


class UnifiedLLMProvider:
    """
    Unified provider for all LLM APIs
    Routes requests to correct API based on provider config
    """
    
    def __init__(self, provider_config: Dict[str, Any]):
        """
        Initialize with provider configuration
        
        Args:
            provider_config: Config dict with api_key, base_url, provider_type, etc.
        """
        self.api_key = provider_config["api_key"]
        self.base_url = provider_config["base_url"]
        self.provider_type = provider_config.get("provider_type", "openai_compatible")
        self.timeout = provider_config.get("request_timeout", 30)
        self.provider_name = provider_config.get("name", "Unknown")
    
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using appropriate API"""
        
        start_time = time.time()
        
        try:
            if self.provider_type == "gemini":
                response = self._call_gemini(prompt, model, temperature, max_tokens, system_prompt)
            else:  # openai_compatible (Groq, Mistral, OpenRouter, Cerebras)
                response = self._call_openai_compatible(prompt, model, temperature, max_tokens, system_prompt)
            
            elapsed = (time.time() - start_time) * 1000
            response["response_time_ms"] = elapsed
            return response
        
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return {
                "success": False,
                "content": "",
                "provider": self.provider_name,
                "model": model,
                "error": str(e),
                "response_time_ms": elapsed,
                "usage": None
            }
    
    def _call_gemini(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call Google Gemini API"""
        
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Build request for Gemini
        parts = []
        if system_prompt:
            parts.append({"text": f"System: {system_prompt}\n\nUser: {prompt}"})
        else:
            parts.append({"text": prompt})
        
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                
                usage = None
                if "usageMetadata" in data:
                    usage = {
                        "prompt_tokens": data["usageMetadata"].get("promptTokenCount", 0),
                        "completion_tokens": data["usageMetadata"].get("candidatesTokenCount", 0),
                    }
                
                return {
                    "success": True,
                    "content": content,
                    "provider": self.provider_name,
                    "model": model,
                    "usage": usage,
                    "error": None
                }
            else:
                raise Exception("No candidates in Gemini response")
        else:
            raise Exception(f"Gemini API error: Status {response.status_code}")
    
    def _call_openai_compatible(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call OpenAI-compatible API (Groq, Mistral, OpenRouter, Cerebras)"""
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                
                usage = None
                if "usage" in data:
                    usage = {
                        "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                        "completion_tokens": data["usage"].get("completion_tokens", 0),
                    }
                
                return {
                    "success": True,
                    "content": content,
                    "provider": self.provider_name,
                    "model": model,
                    "usage": usage,
                    "error": None
                }
            else:
                raise Exception("No choices in API response")
        else:
            raise Exception(f"API error: Status {response.status_code} - {response.text}")
