from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel


class StageResult(BaseModel):
    """Base result for any processing stage"""
    stage_name: str
    success: bool
    data: Any
    metadata: Optional[Dict] = None
    warnings: Optional[List[str]] = None
    processing_time_ms: float = 0.0


class AnalysisResult(StageResult):
    """Result from Analyzer stage"""
    confidence: float
    metrics: Optional[Dict] = None


class ValidationResult(StageResult):
    """Result from Validator stage"""
    is_valid: bool
    issues: Optional[List[str]] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None


class ProcessingResult(StageResult):
    """Result from Processor stage"""
    processed_data: Any


class EnhancedResult(StageResult):
    """Result from AI Enhancement stage"""
    enhancement_applied: bool
    model_used: Optional[str] = None


class EngineResponse(BaseModel):
    """Base response contract for all engines"""
    success: bool
    engine_type: str  # "prompt", "debug", "documentation"
    analysis: Optional[AnalysisResult] = None
    validation: Optional[ValidationResult] = None
    processing: Optional[ProcessingResult] = None
    enhancement: Optional[EnhancedResult] = None
    confidence_score: float
    metadata: Optional[Dict] = None
    warnings: Optional[List[str]] = None
    next_actions: Optional[List[Dict]] = None
    processing_time_ms: float = 0.0
    generated_at: datetime = None
    
    def __init__(self, **data):
        if data.get('generated_at') is None:
            data['generated_at'] = datetime.utcnow()
        super().__init__(**data)


class ProcessingStage(ABC):
    """Base class for all processing stages"""
    
    stage_name: str
    
    @abstractmethod
    def execute(self, input_data: Any) -> StageResult:
        """Execute this processing stage"""
        pass


class InputAdapter(ProcessingStage):
    """Converts raw input to canonical model"""
    stage_name = "input_adapter"
    
    @abstractmethod
    def adapt(self, raw_input: Any) -> Any:
        """Adapt raw input to canonical model"""
        pass
    
    def execute(self, input_data: Any) -> StageResult:
        canonical = self.adapt(input_data)
        return StageResult(
            stage_name=self.stage_name,
            success=True,
            data=canonical,
        )


class Analyzer(ProcessingStage):
    """Analyzes canonical model"""
    stage_name = "analyzer"
    
    @abstractmethod
    def analyze(self, canonical_model: Any) -> Dict:
        """Analyze the canonical model"""
        pass
    
    def execute(self, input_data: Any) -> AnalysisResult:
        analysis = self.analyze(input_data)
        return AnalysisResult(
            stage_name=self.stage_name,
            success=True,
            data=analysis,
            confidence=analysis.get("confidence", 0.5),
        )


class Validator(ProcessingStage):
    """Validates analysis and determines if clarification needed"""
    stage_name = "validator"
    
    @abstractmethod
    def validate(self, analysis: Dict) -> Dict:
        """Validate analysis"""
        pass
    
    def execute(self, input_data: Any) -> ValidationResult:
        validation = self.validate(input_data)
        return ValidationResult(
            stage_name=self.stage_name,
            success=True,
            data=validation,
            is_valid=not validation.get("needs_clarification", False),
            needs_clarification=validation.get("needs_clarification", False),
            clarification_question=validation.get("clarification_question"),
        )


class Processor(ProcessingStage):
    """Main processing logic (optimize, diagnose, generate, etc.)"""
    stage_name = "processor"
    
    @abstractmethod
    def process(self, canonical_model: Any, analysis: Dict) -> Any:
        """Process the canonical model"""
        pass
    
    def execute(self, input_data: Any) -> ProcessingResult:
        canonical, analysis = input_data
        processed = self.process(canonical, analysis)
        return ProcessingResult(
            stage_name=self.stage_name,
            success=True,
            data=processed,
            processed_data=processed,
        )


class AIEnhancer(ProcessingStage):
    """Optional AI enhancement"""
    stage_name = "ai_enhancer"
    
    @abstractmethod
    def enhance(self, processed_data: Any) -> Any:
        """Enhance with AI"""
        pass
    
    def execute(self, input_data: Any) -> EnhancedResult:
        enhanced = self.enhance(input_data)
        return EnhancedResult(
            stage_name=self.stage_name,
            success=True,
            data=enhanced,
            enhancement_applied=True,
        )


class Formatter(ProcessingStage):
    """Formats result into structured response"""
    stage_name = "formatter"
    
    @abstractmethod
    def format(self, data: Any) -> EngineResponse:
        """Format into structured response"""
        pass
    
    def execute(self, input_data: Any) -> StageResult:
        response = self.format(input_data)
        return StageResult(
            stage_name=self.stage_name,
            success=True,
            data=response,
        )


class Engine(ABC):
    """Base engine interface"""
    
    engine_type: str
    
    def __init__(self):
        self.input_adapter: Optional[InputAdapter] = None
        self.analyzer: Optional[Analyzer] = None
        self.validator: Optional[Validator] = None
        self.processor: Optional[Processor] = None
        self.ai_enhancer: Optional[AIEnhancer] = None
        self.formatter: Optional[Formatter] = None
    
    def parse(self, raw_input: Any) -> Any:
        """Stage 1: Parse raw input to canonical model"""
        if not self.input_adapter:
            raise NotImplementedError("input_adapter not configured")
        result = self.input_adapter.execute(raw_input)
        return result.data
    
    def analyze(self, canonical_model: Any) -> AnalysisResult:
        """Stage 2: Analyze canonical model"""
        if not self.analyzer:
            raise NotImplementedError("analyzer not configured")
        return self.analyzer.execute(canonical_model)
    
    def validate(self, analysis: Dict) -> ValidationResult:
        """Stage 3: Validate analysis"""
        if not self.validator:
            return ValidationResult(
                stage_name="validator",
                success=True,
                data=analysis,
                is_valid=True,
            )
        return self.validator.execute(analysis)
    
    def process(self, canonical_model: Any, analysis: Dict) -> ProcessingResult:
        """Stage 4: Process"""
        if not self.processor:
            raise NotImplementedError("processor not configured")
        return self.processor.execute((canonical_model, analysis))
    
    def enhance(self, processed_data: Any) -> Optional[EnhancedResult]:
        """Stage 5: AI Enhancement (optional)"""
        if not self.ai_enhancer:
            return None
        return self.ai_enhancer.execute(processed_data)
    
    def format(self, data: Any) -> EngineResponse:
        """Stage 6: Format response"""
        if not self.formatter:
            raise NotImplementedError("formatter not configured")
        result = self.formatter.execute(data)
        return result.data
    
    def respond(
        self,
        raw_input: Any,
        apply_enhancement: bool = True,
    ) -> EngineResponse:
        """Execute full pipeline"""
        import time
        start_time = time.time()
        
        try:
            # Stage 1: Parse
            canonical = self.parse(raw_input)
            
            # Stage 2: Analyze
            analysis_result = self.analyze(canonical)
            
            # Stage 3: Validate
            validation_result = self.validate(analysis_result.data)
            
            # Check if clarification needed
            if validation_result.needs_clarification:
                return EngineResponse(
                    success=False,
                    engine_type=self.engine_type,
                    analysis=analysis_result,
                    validation=validation_result,
                    confidence_score=analysis_result.confidence,
                    warnings=["Clarification needed"],
                    processing_time_ms=(time.time() - start_time) * 1000,
                )
            
            # Stage 4: Process
            processing_result = self.process(canonical, analysis_result.data)
            
            # Stage 5: Enhance (optional)
            enhancement_result = None
            enhanced_data = processing_result.data
            if apply_enhancement:
                enhancement_result = self.enhance(processing_result.data)
                if enhancement_result:
                    enhanced_data = enhancement_result.data
            
            # Stage 6: Format
            response = self.format(enhanced_data)
            
            # Merge metadata
            response.analysis = analysis_result
            response.validation = validation_result
            response.processing = processing_result
            response.enhancement = enhancement_result
            response.processing_time_ms = (time.time() - start_time) * 1000
            
            return response
        
        except Exception as e:
            return EngineResponse(
                success=False,
                engine_type=self.engine_type,
                confidence_score=0.0,
                warnings=[str(e)],
                processing_time_ms=(time.time() - start_time) * 1000,
            )
