"""
Debug Engine Models - All debug-specific data structures
This is the single source of truth for all debug engine types and schemas
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# TYPE DEFINITIONS (Enums/Literals)
# ============================================================================

ArtifactType = Literal[
    "python_traceback",
    "nodejs_error",
    "java_stack_trace",
    "docker_logs",
    "kubernetes_logs",
    "sql_error",
    "git_conflict",
    "http_error",
    "rest_error",
    "json_error",
    "terminal_output",
    "compiler_error",
    "runtime_exception",
    "build_logs",
    "ci_cd_logs",
    "yaml_error",
    "javascript_error",
    "typescript_error",
    "go_error",
    "rust_error",
    "unknown",
]

Language = Literal[
    "python",
    "javascript",
    "typescript",
    "java",
    "go",
    "rust",
    "csharp",
    "php",
    "ruby",
    "sql",
    "yaml",
    "json",
    "bash",
    "docker",
    "kubernetes",
    "terraform",
    "unknown",
]

ErrorCategory = Literal[
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
    "performance_issue",
    "unknown",
]

Severity = Literal["critical", "high", "medium", "low", "info"]

RelatedArtifactType = Literal[
    "code",
    "config",
    "log",
    "schema",
    "requirements",
    "env",
    "dockerfile",
    "manifest",
    "query",
]


# ============================================================================
# INPUT MODELS
# ============================================================================

class DebugArtifact(BaseModel):
    """Raw error artifact submitted by user"""
    content: str
    language_hint: Optional[str] = None
    framework_hint: Optional[str] = None
    context: Optional[str] = None
    artifact_type: Optional[str] = None
    original_input: Optional[dict] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class RelatedArtifact(BaseModel):
    """Supporting artifact (code, config, schema, etc.) for multi-artifact debugging"""
    artifact_type: RelatedArtifactType
    filename: Optional[str] = None
    language: Optional[str] = None
    content: str
    description: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class MultiArtifactDebugInput(BaseModel):
    """Multiple artifacts submitted together for richer debugging context"""
    primary_artifact: DebugArtifact
    related_artifacts: List[RelatedArtifact] = []
    
    def has_related_artifacts(self) -> bool:
        """Check if there are supporting artifacts"""
        return len(self.related_artifacts) > 0
    
    def get_artifacts_by_type(self, artifact_type: RelatedArtifactType) -> List[RelatedArtifact]:
        """Get all artifacts of a specific type"""
        return [a for a in self.related_artifacts if a.artifact_type == artifact_type]
    
    def get_code_artifacts(self) -> List[RelatedArtifact]:
        """Get all code artifacts"""
        return self.get_artifacts_by_type("code")
    
    def get_config_artifacts(self) -> List[RelatedArtifact]:
        """Get all config artifacts"""
        return self.get_artifacts_by_type("config")


# ============================================================================
# ANALYSIS MODELS
# ============================================================================

class AnalysisMetadata(BaseModel):
    """Metadata from Debug Analyzer"""
    artifact_type: ArtifactType
    language: Language
    framework: Optional[str] = None
    category: ErrorCategory
    severity: Severity
    confidence: float
    detected_patterns: List[str] = []
    line_numbers: Optional[List[int]] = None
    error_message: Optional[str] = None
    stack_trace_present: bool = False
    is_compile_time: bool = False


class ClarificationRequest(BaseModel):
    """Request for user clarification"""
    needs_clarification: bool
    question: str
    examples: Optional[List[str]] = None
    follow_up: Optional[str] = None


class DebugContext(BaseModel):
    """Enriched context for the error"""
    related_imports: List[str] = []
    framework_version: Optional[str] = None
    related_configs: List[str] = []
    similar_errors: List[str] = []
    documentation_links: List[str] = []
    previous_context: Optional[str] = None
    from_multi_artifact: Optional[dict] = None


class DebugStrategy(BaseModel):
    """Strategy for analyzing this specific error type"""
    strategy_type: str
    focus_areas: List[str]
    recommended_checks: List[str]
    likely_causes: List[str]
    documentation_sections: List[str]


# ============================================================================
# RESPONSE/OUTPUT MODELS
# ============================================================================

class RootCauseAnalysis(BaseModel):
    """Root cause diagnosis"""
    summary: str
    root_cause: str
    why_it_happened: str
    contributing_factors: List[str] = []
    confidence: float


class Solution(BaseModel):
    """Recommended solution"""
    steps: List[str]
    corrected_code: Optional[str] = None
    corrected_config: Optional[str] = None
    dependencies_to_add: List[str] = []
    commands_to_run: List[str] = []


class LearningContent(BaseModel):
    """Educational content"""
    concept_explained: str
    common_mistakes: List[str] = []
    prevention_strategies: List[str] = []
    mental_model: Optional[str] = None
    best_practices: List[str] = []


class DebugResponse(BaseModel):
    """Complete debug response"""
    success: bool = True
    engine_type: str = "debug"
    analysis: AnalysisMetadata
    diagnosis: RootCauseAnalysis
    solution: Solution
    learning: Optional[LearningContent] = None
    resources: List[str] = []
    next_actions: List[str] = []
    confidence_score: float
    learning_mode: bool = False
    validation: Optional[dict] = None
    processing: Optional[dict] = None
    processing_time_ms: float = 0.0
