"""
Debug Intelligence Engine - Full debugging pipeline
Supports both single-artifact and multi-artifact debugging
"""
from typing import Dict, Any
from .. import processing_framework
from .debug_input_adapter import DebugInputAdapter
from .debug_analyzer import DebugAnalyzer
from .debug_validator import DebugValidator
from .debug_processor import DebugProcessor
from .debug_formatter import DebugFormatter
from .debug_models import MultiArtifactDebugInput, DebugArtifact
from typing import cast


class DebugEngine(processing_framework.Engine):
    """
    Debug Intelligence Engine - helps developers understand and fix errors
    
    Pipeline:
    1. Input Adapter: Normalize error/log to DebugArtifact or MultiArtifactDebugInput
    2. Analyzer: Classify and score error
    3. Validator: Check if clarification needed
    4. Processor: Generate diagnosis and solutions
    5. Formatter: Structure into DebugResponse
    
    Supports:
    - Single artifact: Just the error/traceback/log
    - Multi-artifact: Error + code + config + schema together
    """
    
    engine_type = "debug"
    
    def __init__(self):
        super().__init__()
        
        # Configure stages
        self.input_adapter = DebugInputAdapter()
        self.analyzer = DebugAnalyzer()
        self.validator = DebugValidator()
        
        # Initialize LLM service for processor
        from ..llm.llm_service import LLMService
        llm_service = LLMService()
        self.processor = DebugProcessor(llm_service=llm_service)
        self.formatter = DebugFormatter()
        
        # Debug engine doesn't use AI enhancement in v1
        self.ai_enhancer = None
    
    def respond(
        self,
        raw_input: Dict[str, Any] | str,
        apply_enhancement: bool = False,
        learning_mode: bool = False,
    ):
        """
        Execute full debug pipeline
        
        Supports:
        - Single artifact: raw_input as string or dict with 'content'/'error'
        - Multi-artifact: raw_input dict with 'primary_artifact' and 'related_artifacts'
        """
        
        # Store learning mode in processing context
        self._learning_mode = learning_mode
        
        # Call parent respond but override formatter call to pass extra context
        import time
        start_time = time.time()
        
        try:
            # Stage 1: Parse (supports both single and multi-artifact)
            # Cast input_adapter to DebugInputAdapter to access adapt_multi
            debug_adapter = self.input_adapter
            assert isinstance(debug_adapter, DebugInputAdapter)
            
            # Convert string to dict if needed
            if isinstance(raw_input, str):
                canonical = debug_adapter.adapt(raw_input)
            else:
                # Use adapt_multi for dict input (handles both single and multi)
                canonical = debug_adapter.adapt_multi(raw_input)
            
            # Stage 2: Analyze
            analysis_result = self.analyze(canonical)
            
            # Stage 3: Validate
            validation_result = self.validate(analysis_result.data)
            
            # Check if clarification needed
            if validation_result.needs_clarification:
                return processing_framework.EngineResponse(
                    success=False,
                    engine_type=self.engine_type,
                    analysis=analysis_result,
                    validation=validation_result,
                    confidence_score=analysis_result.confidence,
                    warnings=["Clarification needed"],
                    processing_time_ms=(time.time() - start_time) * 1000,
                )
            
            # Stage 4: Process (with analysis data for context)
            assert self.processor is not None
            processing_result = self.processor.execute((canonical, analysis_result.data))
            
            # Stage 4B: Optional LLM Enhancement (only if low confidence)
            if apply_enhancement:
                confidence = processing_result.data.get("confidence", 1.0)
                need_llm = processing_result.data.get("need_llm", False)
                
                # Only call LLM if confidence is low
                if need_llm or confidence < 0.7:
                    try:
                        error_artifact = canonical.content if isinstance(canonical, DebugArtifact) else str(canonical)
                        processor = cast(DebugProcessor, self.processor)
                        enhanced_result = processor.enhance_with_llm(
                            processing_result.data,
                            analysis_result.data,
                            error_artifact
                        )
                        processing_result.data = enhanced_result
                        processing_result.data["llm_enhanced"] = True
                    except Exception as e:
                        print(f"LLM enhancement failed: {e}")
                        processing_result.data["llm_enhanced"] = False
            
            # Stage 5: Format (with processing results)
            format_input = {
                "analysis": analysis_result.data,
                "processing": processing_result.data,
                "learning_mode": learning_mode,
            }
            assert self.formatter is not None
            response = self.formatter.format(format_input)
            
            # Merge metadata
            response.analysis = analysis_result
            response.validation = validation_result
            response.processing = processing_result
            response.processing_time_ms = (time.time() - start_time) * 1000
            
            # Add multi-artifact context if available
            if isinstance(canonical, MultiArtifactDebugInput):
                if canonical.has_related_artifacts():
                    if not response.validation:
                        response.validation = {}
                    if isinstance(response.validation, dict):
                        response.validation["multi_artifact_context"] = {
                            "code_artifacts": len(canonical.get_code_artifacts()),
                            "config_artifacts": len(canonical.get_config_artifacts()),
                            "total_related": len(canonical.related_artifacts),
                        }
            
            return response
        
        except Exception as e:
            return processing_framework.EngineResponse(
                success=False,
                engine_type=self.engine_type,
                confidence_score=0.0,
                warnings=[str(e)],
                processing_time_ms=(time.time() - start_time) * 1000,
            )
