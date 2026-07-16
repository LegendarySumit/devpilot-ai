"""
Prompt Formatter - Formats processing result into PromptResponse
"""
from typing import Dict, Any, List
from app.models.prompt_models import (
    PromptResponse,
    PromptAnalysis,
    PromptScore,
    NextAction,
    Clarification,
)
from app.services.processing_framework import Formatter, EngineResponse


class PromptFormatter(Formatter):
    """Formats prompt processing results into structured PromptResponse"""
    
    stage_name = "prompt_formatter"
    
    def format(self, data: Dict[str, Any]) -> EngineResponse:
        """Format processing result into PromptResponse"""
        
        # Extract data from processing pipeline
        enhanced_prompt = data.get("enhanced_prompt") or data.get("optimized_prompt", "")
        optimized_prompt = data.get("optimized_prompt", "")
        analysis_data = data.get("analysis", {})
        confidence = analysis_data.get("confidence", 0.85)
        
        # Calculate score
        prompt_score = self._calculate_score(analysis_data)
        
        # Create analysis
        analysis = PromptAnalysis(
            score=analysis_data.get("score", 70),
            weak_areas=analysis_data.get("weak_areas", []),
            improvements_applied=data.get("improvements_applied", []),
            confidence=confidence,
        )
        
        # Create why_better explanations
        why_better = self._generate_why_better(analysis_data, data.get("improvements_applied", []))
        
        # Create next actions
        next_actions = self._generate_next_actions(analysis_data)
        
        # Create response
        response = PromptResponse(
            success=True,
            analysis=analysis,
            optimized_prompt=enhanced_prompt or optimized_prompt,
            prompt_score=prompt_score,
            improvements_summary=data.get("improvements_applied", []),
            why_better=why_better,
            next_actions=next_actions,
            confidence_score=confidence,
        )
        
        return response
    
    def _calculate_score(self, analysis_data: Dict[str, Any]) -> PromptScore:
        """Calculate detailed prompt score"""
        
        base_score = analysis_data.get("score", 70) / 100.0
        weak_areas = analysis_data.get("weak_areas", [])
        metrics = analysis_data.get("metrics", {})
        
        clarity = 0.8 if metrics.get("has_goal") else 0.5
        context = 0.9 if metrics.get("has_context") else 0.4
        constraints = 0.85 if metrics.get("has_constraints") else 0.3
        output_format = 0.9 if metrics.get("has_output_format") else 0.4
        
        return PromptScore(
            overall=base_score,
            clarity=clarity,
            context=context,
            constraints=constraints,
            output_format=output_format,
            metrics={
                "weak_area_count": len(weak_areas),
                "improvement_count": len(analysis_data.get("improvements_applied", [])),
                "completeness": analysis_data.get("completeness", 0.5),
                "ambiguity": analysis_data.get("ambiguity", 0.5),
            },
        )
    
    def _generate_why_better(self, analysis_data: Dict[str, Any], improvements: List[str]) -> List[str]:
        """Generate structured explanations for improvements"""
        
        explanations = []
        metrics = analysis_data.get("metrics", {})
        
        if metrics.get("has_context") or "Added project context" in improvements:
            explanations.append("More explicit task context helps models understand intent and scope")
        
        if metrics.get("has_constraints") or "constraint" in str(improvements).lower():
            explanations.append("Clear constraints reduce ambiguous outputs and improve relevance")
        
        if metrics.get("has_output_format") or "output format" in str(improvements).lower():
            explanations.append("Defined output format improves downstream usability and parsing")
        
        if "Added professional role" in improvements:
            explanations.append("Expert role/context sets expectations and improves response quality")
        
        if metrics.get("has_examples") or "example" in str(improvements).lower():
            explanations.append("Examples reduce ambiguity and guide output style")
        
        if not explanations:
            explanations.append("Structured prompts yield more consistent and relevant responses")
        
        return explanations
    
    def _generate_next_actions(self, analysis_data: Dict[str, Any]) -> List[NextAction]:
        """Generate recommended next actions"""
        
        actions = []
        score = analysis_data.get("score", 70)
        
        actions.append(NextAction(
            label="Copy optimized prompt",
            action_type="copy",
            description="Copy to clipboard for immediate use",
        ))
        
        if score < 80:
            actions.append(NextAction(
                label="Refine further",
                action_type="refine",
                description="Address remaining weak areas",
            ))
        
        actions.append(NextAction(
            label="Export for target model",
            action_type="export",
            description="Format for ChatGPT, Claude, Gemini, etc.",
        ))
        
        actions.append(NextAction(
            label="Share with team",
            action_type="share",
            description="Generate shareable link",
        ))
        
        return actions
