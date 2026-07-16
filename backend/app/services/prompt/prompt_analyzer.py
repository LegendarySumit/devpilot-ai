"""
Prompt Analyzer - Analyzes CanonicalPromptSpecification
"""
from typing import Dict, Any
from app.models.canonical_prompt_specification import CanonicalPromptSpecification
from app.services.processing_framework import Analyzer, AnalysisResult


class PromptAnalyzer(Analyzer):
    """Analyzes canonical prompt specification for quality and completeness"""
    
    stage_name = "prompt_analyzer"
    
    def analyze(self, canonical_model: CanonicalPromptSpecification) -> Dict[str, Any]:
        """Analyze prompt specification"""
        
        weak_areas = []
        metrics = {}
        
        # Check goal
        has_goal = bool(canonical_model.goal and len(canonical_model.goal.strip()) > 5)
        if not has_goal:
            weak_areas.append("Missing Goal")
        metrics["has_goal"] = has_goal
        
        # Check context
        has_context = bool(canonical_model.context and len(canonical_model.context.strip()) > 10)
        if not has_context:
            weak_areas.append("Missing Context")
        metrics["has_context"] = has_context
        
        # Check constraints
        has_constraints = len(canonical_model.constraints) > 0
        if not has_constraints:
            weak_areas.append("Missing Constraints")
        metrics["has_constraints"] = has_constraints
        metrics["constraint_count"] = len(canonical_model.constraints)
        
        # Check output format
        has_output = bool(canonical_model.expected_output and len(canonical_model.expected_output.strip()) > 5)
        if not has_output:
            weak_areas.append("Missing Output Format")
        metrics["has_output_format"] = has_output
        
        # Check examples
        has_examples = len(canonical_model.examples) > 0
        metrics["has_examples"] = has_examples
        
        # Calculate score
        completeness = sum([
            has_goal,
            has_context,
            has_constraints,
            has_output,
            has_examples,
        ]) / 5.0
        
        score = int(40 + (completeness * 60))
        
        # Calculate confidence based on clarity and completeness
        confidence = 0.5
        if score >= 80:
            confidence = 0.95
        elif score >= 70:
            confidence = 0.85
        elif score >= 50:
            confidence = 0.65
        
        # Check for ambiguity
        ambiguity = self._calculate_ambiguity(canonical_model)
        metrics["ambiguity_score"] = ambiguity
        
        return {
            "score": score,
            "confidence": confidence,
            "weak_areas": weak_areas,
            "metrics": metrics,
            "completeness": completeness,
            "ambiguity": ambiguity,
        }
    
    def _calculate_ambiguity(self, canonical: CanonicalPromptSpecification) -> float:
        """Calculate ambiguity score (0-1, higher = more ambiguous)"""
        
        ambiguity = 0.0
        
        # Single word goal is very ambiguous
        goal_words = len(canonical.goal.split()) if canonical.goal else 0
        if goal_words <= 2:
            ambiguity += 0.3
        elif goal_words <= 5:
            ambiguity += 0.15
        
        # No context = ambiguous
        if not canonical.context:
            ambiguity += 0.2
        
        # No constraints = ambiguous
        if not canonical.constraints:
            ambiguity += 0.15
        
        # No output format = ambiguous
        if not canonical.expected_output:
            ambiguity += 0.2
        
        return min(1.0, ambiguity)
