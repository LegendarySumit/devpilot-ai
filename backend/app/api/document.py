from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
import json
from app.services.documentation.documentation_engine import DocumentationEngine
from app.models.profile import PREDEFINED_PROFILES
from app.models.theme import PREDEFINED_THEMES

router = APIRouter()
engine = DocumentationEngine()


class ProcessDocumentRequest(BaseModel):
    """Process documentation request through Documentation Engine"""
    input: Dict[str, Any] | str  # Can be idea, github URL, readme, local project
    input_type: Literal["idea", "github", "readme", "local_project"]
    operation: Literal["analyze", "generate"] = "generate"
    theme_id: Optional[str] = None
    profile_id: Optional[str] = None
    document_type: Optional[str] = "README"


class ProjectIdeaRequest(BaseModel):
    idea: str
    profile_id: Optional[str] = None
    theme_id: Optional[str] = None
    document_type: Optional[str] = "README"


class GitHubRequest(BaseModel):
    repo_url: str
    profile_id: Optional[str] = None
    theme_id: Optional[str] = None
    document_type: Optional[str] = "README"
    repo_data: Optional[Dict[str, Any]] = None


class ReadmeRequest(BaseModel):
    content: str
    profile_id: Optional[str] = None
    theme_id: Optional[str] = None
    document_type: Optional[str] = "README"


class LocalProjectRequest(BaseModel):
    project_name: Optional[str] = None
    files: Dict[str, str]
    profile_id: Optional[str] = None
    theme_id: Optional[str] = None
    document_type: Optional[str] = "README"


class DocumentationResponse(BaseModel):
    success: bool
    markdown: str
    profile_id: str
    theme_id: str
    document_type: str
    metadata: Dict[str, Any]


@router.get("/")
def document_status() -> dict[str, str]:
    return {"module": "document", "status": "ready"}


@router.post("/process")
def process_documentation(request: ProcessDocumentRequest):
    """
    Process documentation through the Documentation Engine
    
    Unified endpoint that handles multiple input types (idea, github, readme, local project).
    The engine automatically normalizes the input and generates documentation.
    
    Args:
        input: Raw input content or structured dict
        input_type: Type of input (idea | github | readme | local_project)
        operation: "analyze" | "generate"
        theme_id: ID of theme to use
        profile_id: ID of writing profile
        document_type: Type of document (README, CONTRIBUTING, etc.)
    
    Returns:
        Generated markdown document
    """
    try:
        # Normalize input
        if isinstance(request.input, str):
            normalized_input = {
                "content": request.input,
                "input_type": request.input_type,
            }
        else:
            normalized_input = request.input
            if "input_type" not in normalized_input:
                normalized_input["input_type"] = request.input_type
        
        # Get theme if specified
        theme = None
        if request.theme_id and request.theme_id in PREDEFINED_THEMES:
            theme = PREDEFINED_THEMES[request.theme_id]
        
        # Run engine
        response = engine.respond(normalized_input, theme=theme.dict() if theme else None)
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/profiles")
def get_profiles() -> Dict[str, Dict[str, Any]]:
    """Get all available profiles"""
    return {
        profile_id: {
            "id": profile.id,
            "label": profile.label,
            "description": profile.description,
            "tone": profile.tone,
        }
        for profile_id, profile in PREDEFINED_PROFILES.items()
    }


@router.get("/themes")
def get_themes() -> Dict[str, Dict[str, Any]]:
    """Get all available themes"""
    return {
        theme_id: {
            "id": theme.id,
            "name": theme.name,
            "description": theme.description,
        }
        for theme_id, theme in PREDEFINED_THEMES.items()
    }


@router.post("/generate-from-idea")
def generate_from_idea(request: ProjectIdeaRequest) -> DocumentationResponse:
    """
    [DEPRECATED] Use /process instead
    
    Generate documentation from a project idea description
    
    Args:
        idea: Project idea text
        profile_id: Target profile (recruiter, developer, etc.)
        theme_id: Visual theme
        document_type: Document to generate (README, CONTRIBUTING, etc.)
    """
    try:
        result = orchestrator.generate_documentation(
            input_data=request.idea,
            input_type="project_idea",
            profile_id=request.profile_id,
            theme_id=request.theme_id,
            document_type=request.document_type,
        )
        
        return DocumentationResponse(
            success=True,
            markdown=result["markdown"],
            profile_id=request.profile_id or "developer",
            theme_id=request.theme_id or "professional",
            document_type=request.document_type or "README",
            metadata=result["metadata"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-from-github")
def generate_from_github(request: GitHubRequest) -> DocumentationResponse:
    """
    Generate documentation from a GitHub repository
    
    Args:
        repo_url: GitHub repository URL
        repo_data: Optional pre-fetched repository data
        profile_id: Target profile
        theme_id: Visual theme
        document_type: Document to generate
    """
    try:
        input_data = request.repo_data or {"repo_url": request.repo_url}
        
        if "repo_url" not in input_data:
            input_data["repo_url"] = request.repo_url
        
        result = orchestrator.generate_documentation(
            input_data=input_data,
            input_type="github_repository",
            profile_id=request.profile_id,
            theme_id=request.theme_id,
            document_type=request.document_type,
        )
        
        return DocumentationResponse(
            success=True,
            markdown=result["markdown"],
            profile_id=request.profile_id or "developer",
            theme_id=request.theme_id or "professional",
            document_type=request.document_type or "README",
            metadata=result["metadata"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-from-readme")
def generate_from_readme(request: ReadmeRequest) -> DocumentationResponse:
    """
    Improve or regenerate documentation from existing README
    
    Args:
        content: Current README markdown content
        profile_id: Target profile
        theme_id: Visual theme
        document_type: Document to generate
    """
    try:
        result = orchestrator.generate_documentation(
            input_data=request.content,
            input_type="existing_readme",
            profile_id=request.profile_id,
            theme_id=request.theme_id,
            document_type=request.document_type,
        )
        
        return DocumentationResponse(
            success=True,
            markdown=result["markdown"],
            profile_id=request.profile_id or "developer",
            theme_id=request.theme_id or "professional",
            document_type=request.document_type or "README",
            metadata=result["metadata"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-from-project")
def generate_from_project(request: LocalProjectRequest) -> DocumentationResponse:
    """
    Generate documentation from local project files
    
    Args:
        project_name: Name of the project
        files: Dictionary of filename -> content
        profile_id: Target profile
        theme_id: Visual theme
        document_type: Document to generate
    """
    try:
        input_data = {
            "project_name": request.project_name or "Project",
            "files": request.files,
        }
        
        result = orchestrator.generate_documentation(
            input_data=input_data,
            input_type="local_project",
            profile_id=request.profile_id,
            theme_id=request.theme_id,
            document_type=request.document_type,
        )
        
        return DocumentationResponse(
            success=True,
            markdown=result["markdown"],
            profile_id=request.profile_id or "developer",
            theme_id=request.theme_id or "professional",
            document_type=request.document_type or "README",
            metadata=result["metadata"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch-generate")
def batch_generate_documentation(request: ProjectIdeaRequest) -> Dict[str, str]:
    """
    Generate documentation for all profiles and themes
    
    Args:
        idea: Project idea text
    """
    try:
        results = orchestrator.batch_generate(
            input_data=request.idea,
            input_type="project_idea",
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
