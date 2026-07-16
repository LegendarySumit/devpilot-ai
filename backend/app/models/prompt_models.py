from typing import Optional, List, Literal
from pydantic import BaseModel

PromptTarget = Literal[
    "chatgpt",
    "claude",
    "gemini",
    "copilot",
    "cursor",
    "windsurf",
    "github_copilot",
    "generic",
]


class PromptAnalysis(BaseModel):
    score: float
    weak_areas: List[str]
    improvements_applied: List[str]
    analysis_details: Optional[str] = None
    confidence: float = 0.85


class PromptScore(BaseModel):
    overall: float
    clarity: float = 0.0
    context: float = 0.0
    constraints: float = 0.0
    output_format: float = 0.0
    metrics: Optional[dict] = None


class NextAction(BaseModel):
    label: str
    action_type: Literal["copy", "refine", "export", "share"]
    description: Optional[str] = None


class Clarification(BaseModel):
    needed: bool
    question: str
    examples: Optional[List[str]] = None
    follow_up: Optional[str] = None


class PromptResponse(BaseModel):
    success: bool
    analysis: PromptAnalysis
    optimized_prompt: str
    prompt_score: PromptScore
    improvements_summary: List[str]
    why_better: List[str]
    clarification: Optional[Clarification] = None
    next_actions: List[NextAction]
    target: Optional[PromptTarget] = "generic"
    confidence_score: float


class PromptExportRequest(BaseModel):
    prompt: str
    target: PromptTarget = "generic"
    include_system_message: bool = True


class PromptExportResponse(BaseModel):
    target: PromptTarget
    exported_prompt: str
    system_message: Optional[str] = None
    notes: Optional[str] = None
