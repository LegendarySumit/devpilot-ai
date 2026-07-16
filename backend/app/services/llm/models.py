"""
LLM Service Models - Unified request/response schemas for all providers
Used by Debug, Prompt, and Documentation engines
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    """Unified LLM request across all providers"""
    prompt: str
    provider: Optional[str] = None  # Use default if not specified
    model: Optional[str] = None  # Use default model if not specified
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = None
    system_prompt: Optional[str] = None


class LLMResponse(BaseModel):
    """Unified LLM response from any provider"""
    success: bool
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, int]] = None  # tokens_used, prompt_tokens, completion_tokens
    error: Optional[str] = None
    response_time_ms: float = 0.0


class ProviderConfig(BaseModel):
    """Configuration for a single LLM provider"""
    name: str
    api_key: str
    base_url: str
    default_model: str
    available_models: List[str]
    request_timeout: int = 30
    retry_count: int = 3
    class Config:
        arbitrary_types_allowed = True


class ProviderStatus(BaseModel):
    """Status check for a provider"""
    provider: str
    available: bool
    working_models: List[str]
    failed_models: List[str]
    last_tested: Optional[str] = None
