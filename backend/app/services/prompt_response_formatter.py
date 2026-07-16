from typing import List, Optional
from app.models.prompt_models import (
    PromptResponse,
    PromptAnalysis,
    PromptScore,
    NextAction,
    Clarification,
)


class PromptResponseFormatter:
    """Formats prompt analysis into structured response"""
    
    def format_response(
        self,
        analysis_dict: dict,
        optimized_prompt: str,
        confidence: float = 0.85,
    ) -> PromptResponse | Clarification:
        """Format prompt analysis into structured response"""
        
        # Check if clarification is needed
        if analysis_dict.get("clarification_needed"):
            return Clarification(
                needed=True,
                question=analysis_dict.get("follow_up_question", "Can you provide more details about your use case?"),
                examples=analysis_dict.get("examples", []),
                follow_up=analysis_dict.get("context"),
            )
        
        # Calculate prompt score
        score = self._calculate_score(analysis_dict)
        
        # Create analysis
        analysis = PromptAnalysis(
            score=analysis_dict.get("score", 70),
            weak_areas=analysis_dict.get("weak_areas", []),
            improvements_applied=analysis_dict.get("improvements_applied", []),
            confidence=confidence,
        )
        
        # Create why_better explanations
        why_better = self._generate_why_better(analysis_dict)
        
        # Create next actions
        next_actions = self._generate_next_actions(analysis_dict)
        
        # Create response
        response = PromptResponse(
            success=True,
            analysis=analysis,
            optimized_prompt=optimized_prompt,
            prompt_score=score,
            improvements_summary=analysis.improvements_applied,
            why_better=why_better,
            next_actions=next_actions,
            confidence_score=confidence,
        )
        
        return response
    
    def _calculate_score(self, analysis_dict: dict) -> PromptScore:
        """Calculate detailed prompt score"""
        
        base_score = analysis_dict.get("score", 70) / 100
        weak_areas = analysis_dict.get("weak_areas", [])
        
        clarity = 1.0 if "clarity" not in weak_areas else 0.6
        context = 1.0 if "context" not in weak_areas else 0.5
        constraints = 1.0 if "constraints" not in weak_areas else 0.5
        output_format = 1.0 if "output_format" not in weak_areas else 0.6
        
        return PromptScore(
            overall=base_score,
            clarity=clarity,
            context=context,
            constraints=constraints,
            output_format=output_format,
            metrics={
                "weak_area_count": len(weak_areas),
                "improvement_count": len(analysis_dict.get("improvements_applied", [])),
            },
        )
    
    def _generate_why_better(self, analysis_dict: dict) -> List[str]:
        """Generate explanations for why improvements help"""
        
        explanations = []
        weak_areas = analysis_dict.get("weak_areas", [])
        
        if "Missing Context" in weak_areas or "Context" in analysis_dict.get("improvements_applied", []):
            explanations.append("More explicit task context helps models understand intent and scope")
        
        if "Missing Constraints" in weak_areas or "Constraints" in analysis_dict.get("improvements_applied", []):
            explanations.append("Clear constraints reduce ambiguous outputs and improve relevance")
        
        if "No Output Format" in weak_areas or "Output" in analysis_dict.get("improvements_applied", []):
            explanations.append("Defined output format improves downstream usability and parsing")
        
        if "Missing Project Structure" in weak_areas or "Architecture" in analysis_dict.get("improvements_applied", []):
            explanations.append("Project architecture context enables framework-specific suggestions")
        
        if not explanations:
            explanations.append("Structured prompts yield more consistent and relevant responses")
        
        return explanations
    
    def _generate_next_actions(self, analysis_dict: dict) -> List[NextAction]:
        """Generate recommended next actions"""
        
        actions = []
        
        actions.append(NextAction(
            label="Copy optimized prompt",
            action_type="copy",
            description="Copy to clipboard for immediate use",
        ))
        
        if analysis_dict.get("score", 70) < 80:
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
