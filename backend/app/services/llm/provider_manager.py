"""
Provider Manager - Handles provider selection and fallback logic
"""
from typing import Optional
from .config import LLM_PROVIDERS, WORKING_MODELS, PROVIDER_PRIORITY
from .llm_service import LLMService


class ProviderManager:
    """Manages provider selection with fallback support"""
    
    def __init__(self):
        """Initialize provider manager"""
        self.llm_service = LLMService()
    
    def generate_with_fallback(
        self,
        prompt: str,
        preferred_provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
    ):
        """
        Generate with automatic fallback if provider fails
        
        Tries preferred provider first, then falls back to others
        
        Args:
            prompt: User prompt
            preferred_provider: Provider to try first
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Max tokens
            system_prompt: System message
        
        Returns:
            LLMResponse from first successful provider
        """
        
        # Determine providers to try (in order)
        providers_to_try = []
        
        if preferred_provider:
            if preferred_provider in LLM_PROVIDERS:
                providers_to_try.append(preferred_provider)
        
        # Add remaining providers in priority order
        for provider in PROVIDER_PRIORITY:
            if provider not in providers_to_try:
                providers_to_try.append(provider)
        
        # Try each provider
        last_error = None
        
        for provider_name in providers_to_try:
            try:
                response = self.llm_service.generate(
                    prompt=prompt,
                    provider=provider_name,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt
                )
                
                if response.success:
                    return response
                
                last_error = response.error
            
            except Exception as e:
                last_error = str(e)
                continue
        
        # All providers failed
        from .models import LLMResponse
        return LLMResponse(
            success=False,
            content="",
            provider="fallback_failed",
            model=model or "unknown",
            error=f"All providers failed. Last error: {last_error}"
        )
    
    def get_fastest_provider(self) -> str:
        """Get the fastest provider based on test results"""
        # Based on test results: Groq is fastest at 0.77s
        return "groq"
    
    def get_most_reliable_provider(self) -> str:
        """Get the most reliable provider (all models working)"""
        # Based on test results: Mistral has 4/4 models working
        return "mistral"
    
    def get_provider_recommendations(self):
        """Get recommendations for different use cases"""
        return {
            "fastest": "groq",           # 0.77s response time
            "most_reliable": "mistral",  # 4/4 models working
            "default": "gemini",         # Google Gemini (user preference)
            "best_quality": "openrouter",  # Access to GPT-4o
        }
    
    def get_available_models(self, provider: Optional[str] = None):
        """Get available models, optionally filtered by provider"""
        if provider:
            return {provider: WORKING_MODELS.get(provider, [])}
        return WORKING_MODELS.copy()
