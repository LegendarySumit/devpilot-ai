"""
Prompt Engine - Full prompt optimization pipeline using the processing framework
"""
from typing import Dict, Any, Optional
from app.services.processing_framework import Engine
from app.services.prompt.prompt_input_parser import PromptInputParser
from app.services.prompt.prompt_analyzer import PromptAnalyzer
from app.services.prompt.prompt_validator import PromptValidator
from app.services.prompt.prompt_processor import PromptProcessor
from app.services.prompt.prompt_formatter import PromptFormatter
from app.services.llm import LLMService


class PromptEngine(Engine):
    """
    Prompt Engineering Engine - transforms vague task specs into precise prompts
    
    Pipeline:
    1. Input Parser: Normalize multiple input sources to CanonicalPromptSpecification
    2. Analyzer: Score and identify weak areas
    3. Validator: Check if clarification needed
    4. Processor: Rule-based optimization (two-pass)
    5. AI Enhancer: Polish with LLM (optional)
    6. Formatter: Structure into PromptResponse
    """
    
    engine_type = "prompt"
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__()
        
        # Configure stages
        self.input_adapter = PromptInputParser()
        self.analyzer = PromptAnalyzer()
        self.validator = PromptValidator()
        self.processor = PromptProcessor()
        self.formatter = PromptFormatter()
        
        # Optional AI enhancement
        if llm_service:
            self.llm_service = llm_service
        else:
            self.llm_service = None
    
    def respond(
        self,
        raw_input: Dict[str, Any] | str,
        apply_enhancement: bool = True,
    ):
        """Execute full prompt optimization pipeline"""
        return super().respond(raw_input, apply_enhancement)
