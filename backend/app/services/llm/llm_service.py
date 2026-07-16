"""
LLM Service - Unified interface for all engines (Debug, Prompt, Documentation)
Default provider: Gemini
Users can select any model from any provider
"""
from typing import Optional, Dict, Any
from .models import LLMResponse
from .config import LLM_PROVIDERS, DEFAULT_PROVIDER, WORKING_MODELS, PROVIDER_PRIORITY
from .provider import UnifiedLLMProvider


class LLMService:
    """
    Main LLM Service - Entry point for all engines
    Handles provider selection, model validation, and response formatting
    """
    
    def __init__(self, default_provider: str = DEFAULT_PROVIDER):
        """
        Initialize LLM service
        
        Args:
            default_provider: Provider to use if not specified (default: Gemini)
        """
        self.default_provider = default_provider
        self.providers_cache = {}
    
    def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
    ) -> LLMResponse:
        """
        Generate text using LLM
        
        Args:
            prompt: User prompt/message
            provider: Provider name (uses default if not specified)
            model: Model name (uses default if not specified)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Max tokens in response
            system_prompt: Optional system message
        
        Returns:
            LLMResponse with success, content, usage, error, response_time_ms
        """
        
        # Validate and resolve provider
        provider = provider or self.default_provider
        
        if provider not in LLM_PROVIDERS:
            return LLMResponse(
                success=False,
                content="",
                provider=provider,
                model=model or "unknown",
                error=f"Provider '{provider}' not found. Available: {', '.join(LLM_PROVIDERS.keys())}"
            )
        
        provider_config = LLM_PROVIDERS[provider]
        
        # Validate and resolve model
        model = model or provider_config["default_model"]
        
        if model not in WORKING_MODELS.get(provider, []):
            return LLMResponse(
                success=False,
                content="",
                provider=provider,
                model=model,
                error=f"Model '{model}' not working for provider '{provider}'. Working models: {WORKING_MODELS.get(provider, [])}"
            )
        
        # Get or create provider instance
        provider_instance = self._get_provider(provider)
        
        # Call provider API
        try:
            response_dict = provider_instance.generate(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt
            )
            
            return LLMResponse(**response_dict)
        
        except Exception as e:
            return LLMResponse(
                success=False,
                content="",
                provider=provider,
                model=model,
                error=f"Generation failed: {str(e)}"
            )
    
    def status(self) -> Dict[str, Any]:
        """Get status of all providers and models"""
        
        status = {
            "default_provider": self.default_provider,
            "working_providers": PROVIDER_PRIORITY,
            "providers": {}
        }
        
        for provider_name in LLM_PROVIDERS.keys():
            working_models = WORKING_MODELS.get(provider_name, [])
            status["providers"][provider_name] = {
                "name": LLM_PROVIDERS[provider_name]["name"],
                "default_model": LLM_PROVIDERS[provider_name]["default_model"],
                "working_models": working_models,
                "total_models": len(working_models)
            }
        
        return status
    
    def list_working_models(self) -> Dict[str, list]:
        """List all working models by provider"""
        return WORKING_MODELS.copy()
    
    def set_default_provider(self, provider: str) -> bool:
        """Change default provider"""
        if provider not in LLM_PROVIDERS:
            return False
        self.default_provider = provider
        return True
    
    def _get_provider(self, provider_name: str) -> UnifiedLLMProvider:
        """Get or create provider instance (cached)"""
        
        if provider_name not in self.providers_cache:
            config = LLM_PROVIDERS[provider_name]
            self.providers_cache[provider_name] = UnifiedLLMProvider(config)
        
        return self.providers_cache[provider_name]
