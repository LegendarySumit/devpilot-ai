from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.canonical_project_model import CanonicalProjectModel, Identity


class ExtractionMetadata(dict):
    def __init__(self):
        super().__init__()
        self['confidence_score'] = 0.0
        self['extraction_method'] = ""
        self['fields_with_high_confidence'] = []
        self['fields_with_medium_confidence'] = []
        self['fields_requiring_clarification'] = []
        self['clarification_questions'] = []


class ContextExtractor(ABC):
    """Abstract base class for context extractors"""
    
    @abstractmethod
    def extract(self, input_data: Any) -> tuple[CanonicalProjectModel, ExtractionMetadata]:
        """
        Extract context and return CPM and metadata
        
        Returns:
            Tuple of (CanonicalProjectModel, ExtractionMetadata)
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate if input is suitable for this extractor"""
        pass
    
    def _calculate_confidence(self, filled_fields: int, total_fields: int) -> float:
        """Calculate extraction confidence score"""
        return min(1.0, filled_fields / total_fields) if total_fields > 0 else 0.0
    
    def _mark_field_confidence(self, field: str, confidence: str) -> None:
        """Helper to categorize field confidence"""
        if confidence == "high":
            self.metadata['fields_with_high_confidence'].append(field)
        elif confidence == "medium":
            self.metadata['fields_with_medium_confidence'].append(field)
        else:
            self.metadata['fields_requiring_clarification'].append(field)
    
    def _add_clarification_question(self, field: str, question: str, suggested_answers: list = None) -> None:
        """Add a clarification question"""
        self.metadata['clarification_questions'].append({
            'field': field,
            'question': question,
            'suggested_answers': suggested_answers or []
        })
