"""
Debug Validator - Validates analysis and determines if clarification needed
Incorporates all clarification logic from old implementation
"""
from typing import Dict, Any
from .. import processing_framework


class DebugValidator(processing_framework.Validator):
    """
    Validates debug analysis and checks for clarification needs.
    
    Clarification triggers:
    - Confidence < 0.6: Ask for complete error
    - Artifact type unknown: Ask what type
    - Terminal output < 50 chars: Ask for complete output
    - Content < 20 chars: Ask for more context
    - No error message AND confidence < 0.7: Ask for exact message
    """
    
    stage_name = "debug_validator"
    
    CONFIDENCE_THRESHOLD = 0.65
    
    def validate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis and check if clarification needed"""
        
        confidence = analysis.get("confidence", 0.5)
        artifact_type = analysis.get("artifact_type", "unknown")
        language = analysis.get("language", "unknown")
        error_message = analysis.get("error_message")
        metrics = analysis.get("metrics", {})
        content_length = metrics.get("content_length", 0)
        
        needs_clarification = False
        clarification_question = None
        clarification_examples = []
        clarification_reason = None
        
        # Check 1: Confidence < 0.6
        if confidence < 0.6:
            needs_clarification = True
            clarification_reason = "low_confidence"
            clarification_question = "Can you provide the complete error message or traceback?"
            clarification_examples = [
                "Include the full stack trace",
                "Include all error messages",
                "Include the context where it occurred",
            ]
        
        # Check 2: Unknown artifact type
        elif artifact_type == "unknown":
            needs_clarification = True
            clarification_reason = "unknown_artifact"
            clarification_question = "What type of error is this? (e.g., Python traceback, Node.js error, Docker logs)"
            clarification_examples = [
                "Traceback (most recent call last)...",
                "TypeError: Cannot read property",
                "docker: command not found"
            ]
        
        # Check 3: Terminal output too short
        elif artifact_type == "terminal_output" and content_length < 50:
            needs_clarification = True
            clarification_reason = "insufficient_output"
            clarification_question = "Can you paste the complete terminal output or logs?"
            clarification_examples = [
                "Include any error messages that appear before or after",
                "Include the full command output",
                "Include context around the error"
            ]
        
        # Check 4: Content too short
        elif content_length < 20:
            needs_clarification = True
            clarification_reason = "too_short"
            clarification_question = "Can you provide more context or the complete error?"
            clarification_examples = [
                "The full error message",
                "The surrounding code",
                "The commands you ran"
            ]
        
        # Check 5: No error message AND low confidence
        elif error_message is None and confidence < 0.7:
            needs_clarification = True
            clarification_reason = "no_error_message"
            clarification_question = "What is the exact error message you're seeing?"
            clarification_examples = [
                "Copy the error from your terminal",
                "Include the last few lines of output",
                "Paste the complete traceback"
            ]
        
        return {
            "is_valid": not needs_clarification,
            "needs_clarification": needs_clarification,
            "clarification_question": clarification_question,
            "clarification_examples": clarification_examples,
            "clarification_reason": clarification_reason,
            "confidence": confidence,
            "language": language,
            "artifact_type": artifact_type,
            "content_length": content_length,
        }
