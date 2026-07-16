"""
LLM Configuration - API keys from environment variables
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API KEYS FROM ENVIRONMENT
LLM_API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY", ""),
    "groq": os.getenv("GROQ_API_KEY", ""),
    "mistral": os.getenv("MISTRAL_API_KEY", ""),
    "openrouter": os.getenv("OPENROUTER_API_KEY", ""),
    "cerebras": os.getenv("CEREBRAS_API_KEY", ""),
}

# PROVIDER CONFIGURATIONS
LLM_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "api_key": LLM_API_KEYS["gemini"],
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "default_model": "gemini-2.5-flash",
        "available_models": ["gemini-2.5-flash"],
        "request_timeout": 30,
        "retry_count": 3,
        "provider_type": "gemini"
    },
    "groq": {
        "name": "Groq",
        "api_key": LLM_API_KEYS["groq"],
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "available_models": ["llama-3.3-70b-versatile"],
        "request_timeout": 30,
        "retry_count": 3,
        "provider_type": "openai_compatible"
    },
    "mistral": {
        "name": "Mistral AI",
        "api_key": LLM_API_KEYS["mistral"],
        "base_url": "https://api.mistral.ai/v1",
        "default_model": "mistral-large-latest",
        "available_models": [
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
            "codestral-latest",
        ],
        "request_timeout": 30,
        "retry_count": 3,
        "provider_type": "openai_compatible"
    },
    "openrouter": {
        "name": "OpenRouter",
        "api_key": LLM_API_KEYS["openrouter"],
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "openrouter/auto",
        "available_models": [
            "openrouter/auto",
            "gpt-4o",
            "llama-3.3-70b-instruct",
        ],
        "request_timeout": 30,
        "retry_count": 3,
        "provider_type": "openai_compatible"
    },
    "cerebras": {
        "name": "Cerebras",
        "api_key": LLM_API_KEYS["cerebras"],
        "base_url": "https://api.cerebras.ai/v1",
        "default_model": "gpt-oss-120b",
        "available_models": [
            "gpt-oss-120b",
            "zai-glm-4.7",
        ],
        "request_timeout": 30,
        "retry_count": 3,
        "provider_type": "openai_compatible"
    },
}

PROVIDER_PRIORITY = [
    "groq",
    "mistral",
    "openrouter",
    "cerebras",
    "gemini",
]

DEFAULT_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "groq")

WORKING_MODELS = {
    "gemini": ["gemini-2.5-flash"],
    "groq": ["llama-3.3-70b-versatile"],
    "mistral": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "codestral-latest"],
    "openrouter": ["openrouter/auto", "gpt-4o", "llama-3.3-70b-instruct"],
    "cerebras": ["gpt-oss-120b", "zai-glm-4.7"],
}


def get_provider_config(provider_name: str) -> Dict:
    if provider_name not in LLM_PROVIDERS:
        raise ValueError(f"Provider '{provider_name}' not found. Available: {list(LLM_PROVIDERS.keys())}")
    return LLM_PROVIDERS[provider_name]


def get_working_providers() -> List[str]:
    return PROVIDER_PRIORITY


def get_all_working_models() -> Dict[str, List[str]]:
    return WORKING_MODELS.copy()
