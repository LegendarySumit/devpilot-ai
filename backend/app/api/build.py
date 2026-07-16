from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from app.models.prompt_models import (
    PromptResponse,
    Clarification,
    PromptExportRequest,
    PromptExportResponse,
    PromptTarget,
)
from app.services.prompt.prompt_engine import PromptEngine

router = APIRouter()
engine = PromptEngine()


class ProcessPromptRequest(BaseModel):
    """Process a prompt through the prompt engine"""
    input: Dict[str, Any] | str  # Can be raw prompt, requirement, github issue, etc.
    operation: Literal["analyze", "optimize", "validate"] = "optimize"
    apply_enhancement: bool = True
    source_type: Optional[Literal["raw_prompt", "requirement", "github_issue", "jira_ticket", "description"]] = None
    target_model: Optional[PromptTarget] = "generic"


class OptimizePromptRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
    target_model: Optional[PromptTarget] = "generic"


class OptimizePromptResponseWrapper(BaseModel):
    success: bool
    response: Optional[PromptResponse] = None
    clarification: Optional[Clarification] = None


@router.get("/")
def build_status() -> dict[str, str]:
    return {"module": "build", "status": "ready"}


@router.post("/process")
def process_prompt(request: ProcessPromptRequest):
    """
    Process a prompt through the Prompt Engine
    
    Unified endpoint that handles multiple input types and operations.
    The engine automatically detects the input type and applies the appropriate processing.
    
    Args:
        input: Raw input (can be prompt text, requirement dict, GitHub issue, etc.)
        operation: "analyze" | "optimize" | "validate"
        apply_enhancement: Whether to apply LLM enhancement (default: True)
        source_type: Explicitly specify input type (optional)
        target_model: Target AI model for formatting
    
    Returns:
        PromptResponse with structured results
    """
    try:
        # Normalize input
        if isinstance(request.input, str):
            normalized_input = {
                "content": request.input,
                "source_type": request.source_type or "raw_prompt",
            }
        else:
            normalized_input = request.input
            if "source_type" not in normalized_input and request.source_type:
                normalized_input["source_type"] = request.source_type
        
        # Run engine
        response = engine.respond(normalized_input, apply_enhancement=request.apply_enhancement)
        
        # Add target model if specified
        if request.target_model and hasattr(response, 'target'):
            response.target = request.target_model
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/optimize-prompt")
def optimize_prompt(request: OptimizePromptRequest) -> OptimizePromptResponseWrapper:
    """
    [DEPRECATED] Use /process instead
    
    Analyze and optimize a prompt
    
    Args:
        prompt: The raw prompt to optimize
        context: Optional context about the use case
        target_model: Target AI model (chatgpt, claude, gemini, etc.)
    
    Returns:
        PromptResponse with analysis and optimized prompt,
        or Clarification if more info needed
    """
    try:
        # Convert to new format and call process endpoint
        new_request = ProcessPromptRequest(
            input=request.prompt,
            source_type="raw_prompt",
            operation="optimize",
            target_model=request.target_model,
        )
        
        response = process_prompt(new_request)
        
        # Wrap in backward-compatible response
        return OptimizePromptResponseWrapper(
            success=response.success,
            response=response if response.success else None,
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/export-prompt")
def export_prompt(request: PromptExportRequest) -> PromptExportResponse:
    """
    Export prompt formatted for specific AI model
    
    Args:
        prompt: The prompt to export
        target: Target model (chatgpt, claude, gemini, copilot, cursor, windsurf)
        include_system_message: Include system message if applicable
    
    Returns:
        Exported prompt with model-specific formatting
    """
    try:
        exported = _format_for_target(
            request.prompt,
            request.target,
            request.include_system_message,
        )
        
        return PromptExportResponse(
            target=request.target,
            exported_prompt=exported,
            notes=f"Formatted for {request.target}",
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/examples")
def get_examples() -> dict[str, list]:
    """Get example prompts"""
    return {
        "weak_examples": [
            "Generate code",
            "Write a function",
            "Create a website",
        ],
        "strong_examples": [
            "Generate a Python function that validates email addresses using regex. Requirements: must handle standard email format, reject common invalid patterns, raise ValueError with descriptive message.",
            "Create a React component that displays a filterable product list. Include search, category filters, sorting options. Use TypeScript with proper typing.",
            "Build a FastAPI endpoint for user authentication. Support JWT tokens, refresh tokens, password hashing with bcrypt. Include proper error handling.",
        ],
    }


@router.get("/targets")
def get_export_targets() -> dict[str, dict]:
    """Get supported export targets"""
    return {
        "chatgpt": {
            "name": "ChatGPT",
            "description": "OpenAI ChatGPT",
            "format": "markdown_with_code_blocks",
        },
        "claude": {
            "name": "Claude",
            "description": "Anthropic Claude",
            "format": "structured_xml",
        },
        "gemini": {
            "name": "Google Gemini",
            "description": "Google Gemini",
            "format": "plain_text",
        },
        "copilot": {
            "name": "GitHub Copilot",
            "description": "GitHub Copilot / Code Comments",
            "format": "code_comment",
        },
        "cursor": {
            "name": "Cursor",
            "description": "Cursor IDE",
            "format": "markdown",
        },
        "windsurf": {
            "name": "Windsurf",
            "description": "Codeium Windsurf",
            "format": "markdown",
        },
    }


@router.post("/analyze")
def analyze_prompt(request: OptimizePromptRequest) -> dict:
    """[DEPRECATED] Use /process with operation='analyze' instead"""
    try:
        new_request = ProcessPromptRequest(
            input=request.prompt,
            source_type="raw_prompt",
            operation="analyze",
        )
        response = process_prompt(new_request)
        
        if response.analysis:
            return {
                "score": response.analysis.score,
                "weak_areas": response.analysis.weak_areas,
                "confidence": response.analysis.confidence,
                "metrics": response.analysis.metrics,
            }
        return {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _format_for_target(prompt: str, target: PromptTarget, include_system: bool) -> str:
    """Format prompt for specific target model"""
    
    if target == "claude":
        return f"Human: {prompt}\n\nAssistant:"
    
    elif target == "gemini":
        return prompt
    
    elif target == "copilot":
        return f"// {prompt}"
    
    elif target in ["cursor", "windsurf"]:
        return f"# Instruction\n\n{prompt}"
    
    elif target == "chatgpt":
        if include_system:
            return f"System: You are a helpful assistant.\n\nUser: {prompt}\n\nAssistant:"
        return prompt
    
    else:  # generic
        return prompt
