"""
Documentation Analyzer - Analyzes project model for documentation completeness
"""
from typing import Dict, Any
from app.models.canonical_project_model import CanonicalProjectModel
from app.services.processing_framework import Analyzer


class DocumentationAnalyzer(Analyzer):
    """Analyzes project model for documentation quality"""
    
    stage_name = "documentation_analyzer"
    
    def analyze(self, canonical_model: CanonicalProjectModel) -> Dict[str, Any]:
        """Analyze documentation completeness"""
        
        missing_sections = self._check_missing_sections(canonical_model)
        quality_score = self._calculate_quality_score(canonical_model, missing_sections)
        confidence = self._calculate_confidence(canonical_model)
        
        return {
            "quality_score": quality_score,
            "confidence": confidence,
            "missing_sections": missing_sections,
            "completeness": self._calculate_completeness(canonical_model),
            "metrics": {
                "has_features": bool(canonical_model.features),
                "has_tech_stack": bool(canonical_model.technical_stack and canonical_model.technical_stack.get("languages")),
                "has_installation": bool(canonical_model.installation),
                "has_usage": bool(canonical_model.usage),
                "is_complete": len(missing_sections) == 0,
            },
        }
    
    def _check_missing_sections(self, model: CanonicalProjectModel) -> list[str]:
        """Identify missing or incomplete sections"""
        
        missing = []
        
        # Check identity
        if not model.identity or not model.identity.get("name"):
            missing.append("Project Name")
        if not model.identity or not model.identity.get("description"):
            missing.append("Project Description")
        
        # Check purpose
        if not model.purpose or not model.purpose.get("business_value"):
            missing.append("Business Value/Purpose")
        
        # Check tech stack
        if not model.technical_stack or not model.technical_stack.get("languages"):
            missing.append("Technology Stack")
        
        # Check features
        if not model.features or len(model.features) == 0:
            missing.append("Features List")
        
        # Check installation
        if not model.installation or not model.installation.get("steps"):
            missing.append("Installation Guide")
        
        # Check usage
        if not model.usage:
            missing.append("Usage Examples")
        
        # Check license
        if not model.status or not model.status.get("license"):
            missing.append("License Information")
        
        return missing
    
    def _calculate_quality_score(self, model: CanonicalProjectModel, missing: list[str]) -> int:
        """Calculate documentation quality score (0-100)"""
        
        # Start with 100 and deduct for missing sections
        score = 100
        
        # Each missing section deducts points
        section_penalties = {
            "Project Name": 15,
            "Project Description": 12,
            "Business Value/Purpose": 10,
            "Technology Stack": 12,
            "Features List": 15,
            "Installation Guide": 15,
            "Usage Examples": 10,
            "License Information": 6,
        }
        
        for section in missing:
            score -= section_penalties.get(section, 5)
        
        # Add bonus for completeness
        if len(missing) == 0:
            score = min(100, score + 10)
        
        return max(0, score)
    
    def _calculate_completeness(self, model: CanonicalProjectModel) -> float:
        """Calculate completeness as percentage (0-1)"""
        
        total_sections = 8
        present = 0
        
        if model.identity and model.identity.get("name"):
            present += 1
        if model.identity and model.identity.get("description"):
            present += 1
        if model.purpose and model.purpose.get("business_value"):
            present += 1
        if model.technical_stack and model.technical_stack.get("languages"):
            present += 1
        if model.features and len(model.features) > 0:
            present += 1
        if model.installation and model.installation.get("steps"):
            present += 1
        if model.usage:
            present += 1
        if model.status and model.status.get("license"):
            present += 1
        
        return present / total_sections
    
    def _calculate_confidence(self, model: CanonicalProjectModel) -> float:
        """Calculate confidence in generated documentation"""
        
        confidence = 0.5
        
        # Well-defined identity = higher confidence
        if model.identity and model.identity.get("name") and len(model.identity.get("name", "")) > 3:
            confidence += 0.15
        
        # Tech stack defined = higher confidence
        if model.technical_stack and model.technical_stack.get("languages"):
            confidence += 0.15
        
        # Features defined = higher confidence
        if model.features and len(model.features) >= 3:
            confidence += 0.1
        
        return min(1.0, confidence)
