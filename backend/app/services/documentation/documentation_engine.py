"""
Documentation Engine - Full documentation generation pipeline
"""
from typing import Dict, Any, Optional
from app.services.processing_framework import Engine
from app.services.documentation.documentation_input_adapter import DocumentationInputAdapter
from app.services.documentation.documentation_analyzer import DocumentationAnalyzer
from app.services.documentation.documentation_processor import DocumentationProcessor
from app.services.documentation.documentation_formatter import DocumentationFormatter


class DocumentationEngine(Engine):
    """
    Documentation Engine - generates professional project documentation
    
    Pipeline:
    1. Input Adapter: Normalize multiple input types to CanonicalProjectModel
    2. Analyzer: Assess documentation completeness and quality
    3. Processor: Generate documentation content and assets
    4. Formatter: Render markdown with theme
    """
    
    engine_type = "documentation"
    
    def __init__(self):
        super().__init__()
        
        # Configure stages
        self.input_adapter = DocumentationInputAdapter()
        self.analyzer = DocumentationAnalyzer()
        self.processor = DocumentationProcessor()
        self.formatter = DocumentationFormatter()
        
        # Documentation doesn't use validator or enhancement in v1
        self.validator = None
        self.ai_enhancer = None
    
    def respond(
        self,
        raw_input: Dict[str, Any] | str,
        theme: Optional[Dict[str, Any]] = None,
        apply_enhancement: bool = False,
    ):
        """Execute full documentation pipeline"""
        
        import time
        start_time = time.time()
        
        try:
            # Stage 1: Parse
            canonical = self.parse(raw_input)
            
            # Stage 2: Analyze
            analysis_result = self.analyze(canonical)
            
            # Stage 3: Process
            processing_result = self.processor.execute((canonical, analysis_result.data))
            
            # Stage 4: Format (with theme)
            format_input = {
                "content": processing_result.data.get("content", {}),
                "assets": processing_result.data.get("assets", {}),
                "theme": theme or self._get_default_theme(),
                "quality_score": analysis_result.data.get("quality_score", 70),
                "sections": processing_result.data.get("sections", []),
            }
            response = self.formatter.format(format_input)
            
            # Merge metadata
            response.analysis = analysis_result
            response.processing = processing_result
            response.processing_time_ms = (time.time() - start_time) * 1000
            
            return response
        
        except Exception as e:
            from app.services.processing_framework import EngineResponse
            return EngineResponse(
                success=False,
                engine_type=self.engine_type,
                confidence_score=0.0,
                warnings=[str(e)],
                processing_time_ms=(time.time() - start_time) * 1000,
            )
    
    def _get_default_theme(self) -> Dict[str, Any]:
        """Get default theme configuration"""
        return {
            "name": "professional",
            "show_badges": True,
            "show_toc": False,
            "centered_header": False,
            "emoji_density": "low",
        }
