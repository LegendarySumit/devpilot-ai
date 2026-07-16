"""
Services module - Core abstraction layers and engines
All three engines (Prompt, Debug, Documentation) use this unified interface
"""

# Core Framework
from app.services.processing_framework import (
    Engine,
    Processor,
    Analyzer,
    Validator,
    Formatter,
    InputAdapter,
    EngineResponse,
    AnalysisResult,
    ProcessingResult,
    ValidationResult,
    EnhancedResult,
    StageResult,
)

# Core Services
from app.services.analysis_contract import AnalysisContract
from app.services.classifier_service import ClassifierService
from app.services.context_extractor_base import ContextExtractor, ExtractionMetadata

# Main Engines (Three Pillars of DevPilot)
from app.services.prompt.prompt_engine import PromptEngine
from app.services.debug.debug_engine import DebugEngine
from app.services.documentation.documentation_engine import DocumentationEngine

# LLM Abstraction (Shared by all engines)
from app.services.llm import (
    LLMService,
    ProviderManager,
    LLMRequest,
    LLMResponse,
)

__all__ = [
    # Framework
    "Engine",
    "Processor",
    "Analyzer",
    "Validator",
    "Formatter",
    "InputAdapter",
    "EngineResponse",
    "AnalysisResult",
    "ProcessingResult",
    "ValidationResult",
    "EnhancedResult",
    "StageResult",
    
    # Core Services
    "AnalysisContract",
    "ClassifierService",
    "ContextExtractor",
    "ExtractionMetadata",
    
    # Three Main Engines
    "PromptEngine",
    "DebugEngine",
    "DocumentationEngine",
    
    # LLM Abstraction
    "LLMService",
    "ProviderManager",
    "LLMRequest",
    "LLMResponse",
]
