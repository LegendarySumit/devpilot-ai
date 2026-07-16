from typing import Optional, List
from pydantic import BaseModel


class CanonicalPromptSpecification(BaseModel):
    """Canonical representation of a task specification"""
    goal: str
    context: Optional[str] = None
    constraints: List[str] = []
    input_format: Optional[str] = None
    expected_output: Optional[str] = None
    examples: List[str] = []
    audience: Optional[str] = None
    target_model: Optional[str] = None
    source_type: str  # "raw_prompt", "requirement", "github_issue", "jira_ticket", "description"
    original_text: Optional[str] = None
