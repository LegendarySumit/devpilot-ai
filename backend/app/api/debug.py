from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Union, Dict, Any, Literal
from app.services.debug.debug_models import DebugArtifact, DebugResponse, ClarificationRequest
from app.services.debug.debug_engine import DebugEngine

router = APIRouter()
engine = DebugEngine()


class ProcessDebugRequest(BaseModel):
    """Process error through Debug Engine"""
    input: Dict[str, Any] | str  # Raw error/log or structured dict
    operation: Literal["analyze", "diagnose"] = "diagnose"
    learning_mode: bool = False
    language_hint: Optional[str] = None
    framework_hint: Optional[str] = None


class DebugRequest(BaseModel):
    content: str
    language_hint: Optional[str] = None
    framework_hint: Optional[str] = None
    context: Optional[str] = None
    learning_mode: Optional[bool] = False


class DebugResponseWrapper(BaseModel):
    success: bool
    response: Union[DebugResponse, ClarificationRequest]
    artifact_type: str


@router.get("/")
def debug_status() -> dict[str, str]:
    return {"module": "debug", "status": "ready"}


@router.post("/process")
def process_debug(request: ProcessDebugRequest):
    """
    Process an error through the Debug Engine
    
    Unified endpoint that handles multiple error types and languages.
    The engine automatically detects the artifact type and applies appropriate analysis.
    
    Args:
        input: Raw error/log text or structured dict
        operation: "analyze" | "diagnose"
        learning_mode: Include educational content
        language_hint: Optional explicit language hint
        framework_hint: Optional explicit framework hint
    
    Returns:
        DebugResponse with analysis and solutions
    """
    try:
        # Normalize input
        if isinstance(request.input, str):
            normalized_input = {
                "content": request.input,
                "language_hint": request.language_hint,
                "framework_hint": request.framework_hint,
            }
        else:
            normalized_input = request.input
            if request.language_hint:
                normalized_input["language_hint"] = request.language_hint
            if request.framework_hint:
                normalized_input["framework_hint"] = request.framework_hint
        
        # Run engine
        response = engine.respond(normalized_input, learning_mode=request.learning_mode)
        return response
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze")
def analyze_error(request: DebugRequest) -> DebugResponseWrapper:
    """
    [DEPRECATED] Use /process instead
    
    Analyze an error artifact (traceback, logs, etc.)
    
    Args:
        content: Error message, traceback, or log content
        language_hint: Optional language hint (python, javascript, java, etc.)
        framework_hint: Optional framework hint (fastapi, django, react, etc.)
        context: Optional additional context about the error
        learning_mode: If true, include educational content
    
    Returns:
        DebugResponse with analysis and solution, or ClarificationRequest if more info needed
    """
    try:
        # Convert to new format and call process
        new_request = ProcessDebugRequest(
            input={
                "content": request.content,
                "language_hint": request.language_hint,
                "framework_hint": request.framework_hint,
                "context": request.context,
            },
            learning_mode=request.learning_mode or False,
        )
        
        response = process_debug(new_request)
        
        # Wrap in backward-compatible response
        artifact_type = response.analysis.artifact_type if hasattr(response, 'analysis') else "unknown"
        
        return DebugResponseWrapper(
            success=response.success,
            response=response,
            artifact_type=artifact_type,
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/python-traceback")
def analyze_python_error(request: DebugRequest) -> DebugResponseWrapper:
    """Analyze Python traceback"""
    request.language_hint = "python"
    return analyze_error(request)


@router.post("/javascript-error")
def analyze_javascript_error(request: DebugRequest) -> DebugResponseWrapper:
    """Analyze JavaScript/Node.js error"""
    request.language_hint = "javascript"
    return analyze_error(request)


@router.post("/sql-error")
def analyze_sql_error(request: DebugRequest) -> DebugResponseWrapper:
    """Analyze SQL error"""
    request.language_hint = "sql"
    return analyze_error(request)


@router.post("/docker-error")
def analyze_docker_error(request: DebugRequest) -> DebugResponseWrapper:
    """Analyze Docker error or logs"""
    request.language_hint = "docker"
    return analyze_error(request)


@router.post("/kubernetes-error")
def analyze_kubernetes_error(request: DebugRequest) -> DebugResponseWrapper:
    """Analyze Kubernetes error or logs"""
    request.language_hint = "kubernetes"
    return analyze_error(request)


@router.post("/git-conflict")
def analyze_git_conflict(request: DebugRequest) -> DebugResponseWrapper:
    """Analyze git merge conflict"""
    request.language_hint = "git"
    return analyze_error(request)


@router.get("/error-types")
def get_supported_error_types() -> dict[str, list[str]]:
    """Get list of supported error types"""
    return {
        "artifact_types": [
            "python_traceback",
            "nodejs_error",
            "java_stack_trace",
            "docker_logs",
            "kubernetes_logs",
            "sql_error",
            "git_conflict",
            "http_error",
            "json_error",
            "yaml_error",
            "compiler_error",
            "build_logs",
            "ci_cd_logs",
        ],
        "languages": [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "sql",
        ],
        "error_categories": [
            "runtime_error",
            "syntax_error",
            "type_error",
            "import_error",
            "configuration_error",
            "network_error",
            "database_error",
            "authentication_error",
            "validation_error",
            "merge_conflict",
            "build_error",
            "deployment_error",
        ],
    }


@router.get("/strategies")
def get_debug_strategies() -> dict[str, dict]:
    """Get available debugging strategies"""
    return {
        "python": {
            "description": "Python-specific debugging strategies",
            "supported_categories": ["import_error", "type_error", "syntax_error"],
        },
        "javascript": {
            "description": "JavaScript/TypeScript debugging strategies",
            "supported_categories": ["type_error", "import_error", "async_error"],
        },
        "sql": {
            "description": "SQL and database debugging strategies",
            "supported_categories": ["syntax_error", "constraint_error", "performance"],
        },
        "docker": {
            "description": "Container and deployment debugging strategies",
            "supported_categories": ["build_error", "runtime_error", "configuration_error"],
        },
        "generic": {
            "description": "Generic debugging for any language",
            "supported_categories": ["all"],
        },
    }
