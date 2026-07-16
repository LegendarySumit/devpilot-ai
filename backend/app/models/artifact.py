from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class Artifact(BaseModel):
    """Single artifact in a processing workspace"""
    artifact_id: str
    artifact_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __init__(self, **data):
        if data.get('created_at') is None:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class WorkspaceArtifacts(BaseModel):
    """Multiple artifacts that should be processed together"""
    workspace_id: str
    artifacts: List[Artifact]
    primary_artifact_id: str  # Which artifact is main
    relationship_context: Optional[str] = None  # How artifacts relate
    created_at: datetime = None
    
    def __init__(self, **data):
        if data.get('created_at') is None:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class ThemeMetadata(BaseModel):
    """Theme configuration and capabilities"""
    id: str
    name: str
    description: str
    capabilities: List[str]
    recommended_for: List[str]
    rules: Optional[Dict] = None


class InteractionStyle(BaseModel):
    """How a result should be formatted for interaction"""
    style_id: str
    name: str
    description: str
    format_guidelines: Optional[Dict] = None


class ProviderMapping(BaseModel):
    """Map provider to interaction style"""
    provider: str
    style_id: str
    additional_format_hints: Optional[Dict] = None
