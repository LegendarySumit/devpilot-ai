"""
Prompt Processor - Optimizes prompt specification (two-pass approach)
"""
from typing import Dict, Any, List
from app.models.canonical_prompt_specification import CanonicalPromptSpecification
from app.services.processing_framework import Processor


class PromptProcessor(Processor):
    """Optimizes prompt through two passes: rule-based then AI enhancement"""
    
    stage_name = "prompt_processor"
    
    def process(self, canonical_model: CanonicalPromptSpecification, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process (optimize) prompt specification"""
        
        # Pass 1: Rule-based optimization
        pass1_result = self._rule_based_optimization(canonical_model, analysis)
        
        # Pass 2: Structure for AI enhancement
        pass2_result = self._prepare_for_ai_enhancement(pass1_result, canonical_model)
        
        return pass2_result
    
    def _rule_based_optimization(
        self,
        canonical: CanonicalPromptSpecification,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Pass 1: Deterministic, rule-based optimization"""
        
        optimizations = []
        
        # Section 1: Role/Context
        role_section = "You are a senior software engineer."
        optimizations.append(role_section)
        
        # Section 2: Task (from goal)
        task = f"Task: {canonical.goal}"
        if canonical.context and not canonical.goal.lower().startswith(canonical.context.lower()[:20]):
            task += f"\nContext: {canonical.context}"
        optimizations.append(task)
        
        # Section 3: Constraints
        if canonical.constraints:
            constraints_text = "Constraints:\n" + "\n".join(
                f"- {c}" for c in canonical.constraints
            )
            optimizations.append(constraints_text)
        else:
            # Add default constraints
            default_constraints = [
                "Follow production-safe defaults",
                "Keep implementation modular",
                "Include edge-case handling",
            ]
            constraints_text = "Constraints:\n" + "\n".join(
                f"- {c}" for c in default_constraints
            )
            optimizations.append(constraints_text)
        
        # Section 4: Input Format (if provided)
        if canonical.input_format:
            optimizations.append(f"Input Format: {canonical.input_format}")
        
        # Section 5: Expected Output
        if canonical.expected_output:
            optimizations.append(f"Expected Output:\n{canonical.expected_output}")
        else:
            # Add default output format
            optimizations.append("Expected Output:\n1. Plan\n2. Implementation\n3. Validation checklist")
        
        # Section 6: Examples (if provided)
        if canonical.examples:
            examples_text = "Examples:\n" + "\n".join(
                f"- {ex}" for ex in canonical.examples
            )
            optimizations.append(examples_text)
        
        optimized_prompt = "\n\n".join(optimizations)
        
        return {
            "optimized_prompt": optimized_prompt,
            "improvements_applied": self._generate_improvements(canonical, analysis),
            "pass": 1,
        }
    
    def _prepare_for_ai_enhancement(self, pass1: Dict[str, Any], canonical: CanonicalPromptSpecification) -> Dict[str, Any]:
        """Pass 2: Prepare for AI enhancement"""
        
        return {
            "optimized_prompt": pass1["optimized_prompt"],
            "improvements_applied": pass1["improvements_applied"],
            "canonical_model": canonical,
            "ready_for_enhancement": True,
            "enhancement_focus": self._identify_enhancement_areas(canonical),
        }
    
    def _generate_improvements(self, canonical: CanonicalPromptSpecification, analysis: Dict[str, Any]) -> List[str]:
        """List all improvements applied"""
        
        improvements = []
        
        # Role added
        improvements.append("Added professional role/context")
        
        # Goal
        if canonical.goal:
            improvements.append("Structured task definition")
        
        # Context
        if canonical.context:
            improvements.append("Added project context")
        
        # Constraints
        if canonical.constraints:
            improvements.append(f"Added {len(canonical.constraints)} specific constraints")
        else:
            improvements.append("Added default production-safe constraints")
        
        # Output format
        if canonical.expected_output:
            improvements.append("Defined output format")
        else:
            improvements.append("Added structured output format")
        
        # Examples
        if canonical.examples:
            improvements.append(f"Included {len(canonical.examples)} examples")
        
        return improvements
    
    def _identify_enhancement_areas(self, canonical: CanonicalPromptSpecification) -> List[str]:
        """Identify areas where AI enhancement would help"""
        
        areas = []
        
        # If goal could be clearer
        if len(canonical.goal.split()) < 5:
            areas.append("expand_goal")
        
        # If context is vague
        if not canonical.context or len(canonical.context) < 50:
            areas.append("enhance_context")
        
        # If no examples
        if not canonical.examples:
            areas.append("add_examples")
        
        # If no specific output format
        if not canonical.expected_output:
            areas.append("specify_output")
        
        return areas
