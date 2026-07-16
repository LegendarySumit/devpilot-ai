"""
Prompt Validator - Validates analysis and identifies clarification needs
"""
from typing import Dict, Any
from app.services.processing_framework import Validator


class PromptValidator(Validator):
    """Validates prompt analysis and determines if clarification is needed"""
    
    stage_name = "prompt_validator"
    
    CONFIDENCE_THRESHOLD = 0.70
    
    def validate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis and check for clarification needs"""
        
        score = analysis.get("score", 0)
        confidence = analysis.get("confidence", 0.5)
        weak_areas = analysis.get("weak_areas", [])
        ambiguity = analysis.get("ambiguity", 0.5)
        
        # Determine if we need clarification
        needs_clarification = False
        clarification_question = None
        
        # If confidence is too low, ask for more details
        if confidence < self.CONFIDENCE_THRESHOLD:
            needs_clarification = True
            clarification_question = self._generate_priority_question(weak_areas, analysis)
        
        # If ambiguity is too high despite other factors
        if ambiguity > 0.7:
            needs_clarification = True
            clarification_question = "Can you provide more specific details about what you want to build?"
        
        return {
            "is_valid": not needs_clarification,
            "needs_clarification": needs_clarification,
            "clarification_question": clarification_question,
            "confidence": confidence,
            "score": score,
        }
    
    def _generate_priority_question(self, weak_areas: list[str], analysis: Dict[str, Any]) -> str:
        """Generate priority-based clarification question"""
        
        metrics = analysis.get("metrics", {})
        
        # Priority 1: Goal (most critical)
        if "Missing Goal" in weak_areas or not metrics.get("has_goal"):
            return "What exactly do you want to build or accomplish?"
        
        # Priority 2: Context (very important)
        if "Missing Context" in weak_areas or not metrics.get("has_context"):
            return "Can you provide background information about your project?"
        
        # Priority 3: Output format (critical for usability)
        if "Missing Output Format" in weak_areas or not metrics.get("has_output_format"):
            return "How should the output be formatted or structured?"
        
        # Priority 4: Constraints
        if "Missing Constraints" in weak_areas or not metrics.get("has_constraints"):
            return "Are there any specific requirements or constraints I should follow?"
        
        # Fallback
        return "Can you provide more details about your requirements?"
