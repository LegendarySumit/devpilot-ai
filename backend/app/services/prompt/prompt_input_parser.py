"""
Prompt Input Parser - Normalizes multiple input sources to CanonicalPromptSpecification
"""
from typing import Optional, Dict, Any
import json
import re
from app.models.canonical_prompt_specification import CanonicalPromptSpecification
from app.services.processing_framework import InputAdapter, StageResult


class PromptInputParser(InputAdapter):
    """Converts raw prompt input (multiple formats) to canonical specification"""
    
    stage_name = "prompt_input_parser"
    
    def adapt(self, raw_input: Dict[str, Any] | str) -> CanonicalPromptSpecification:
        """Parse raw input to canonical prompt specification"""
        
        # Handle string input (raw prompt)
        if isinstance(raw_input, str):
            return self._parse_raw_prompt(raw_input)
        
        # Handle dict input with explicit fields
        if isinstance(raw_input, dict):
            source_type = raw_input.get("source_type", "raw_prompt")
            
            if source_type == "raw_prompt":
                return self._parse_raw_prompt(raw_input.get("content", ""))
            elif source_type == "requirement":
                return self._parse_requirement(raw_input)
            elif source_type == "github_issue":
                return self._parse_github_issue(raw_input)
            elif source_type == "jira_ticket":
                return self._parse_jira_ticket(raw_input)
            elif source_type == "description":
                return self._parse_description(raw_input)
        
        # Fallback: treat as raw prompt
        return self._parse_raw_prompt(str(raw_input))
    
    def _parse_raw_prompt(self, text: str) -> CanonicalPromptSpecification:
        """Parse natural language prompt text"""
        text = text.strip()
        
        # Extract key sections if they exist
        goal = self._extract_goal(text)
        context = self._extract_section(text, ["context", "background", "scenario"])
        constraints = self._extract_constraints(text)
        input_format = self._extract_section(text, ["input", "input format", "given"])
        expected_output = self._extract_section(text, ["output", "output format", "return"])
        examples = self._extract_examples(text)
        
        return CanonicalPromptSpecification(
            goal=goal,
            context=context,
            constraints=constraints,
            input_format=input_format,
            expected_output=expected_output,
            examples=examples,
            source_type="raw_prompt",
            original_text=text,
        )
    
    def _parse_requirement(self, data: Dict[str, Any]) -> CanonicalPromptSpecification:
        """Parse requirement document format"""
        return CanonicalPromptSpecification(
            goal=data.get("title", data.get("requirement", "")),
            context=data.get("context", data.get("background")),
            constraints=[
                c for c in data.get("constraints", [])
                if isinstance(c, str)
            ],
            expected_output=data.get("acceptance_criteria", data.get("expected_output")),
            input_format=data.get("input_format"),
            examples=data.get("examples", []),
            source_type="requirement",
            original_text=json.dumps(data),
        )
    
    def _parse_github_issue(self, data: Dict[str, Any]) -> CanonicalPromptSpecification:
        """Parse GitHub issue format"""
        title = data.get("title", "")
        body = data.get("body", "")
        
        # Extract sections from issue body
        context = self._extract_section(body, ["context", "background", "description"])
        constraints = self._extract_constraints(body)
        expected_output = self._extract_section(body, ["acceptance criteria", "expected"])
        
        return CanonicalPromptSpecification(
            goal=title,
            context=context or body,
            constraints=constraints,
            expected_output=expected_output,
            source_type="github_issue",
            original_text=f"{title}\n\n{body}",
        )
    
    def _parse_jira_ticket(self, data: Dict[str, Any]) -> CanonicalPromptSpecification:
        """Parse Jira ticket format"""
        return CanonicalPromptSpecification(
            goal=data.get("summary", data.get("title", "")),
            context=data.get("description", data.get("details")),
            constraints=[
                c for c in data.get("acceptance_criteria", [])
                if isinstance(c, str)
            ],
            source_type="jira_ticket",
            original_text=json.dumps(data),
        )
    
    def _parse_description(self, data: Dict[str, Any]) -> CanonicalPromptSpecification:
        """Parse freeform description"""
        text = data.get("content", data.get("description", ""))
        
        return CanonicalPromptSpecification(
            goal=data.get("title", self._extract_goal(text)),
            context=text,
            constraints=data.get("constraints", []),
            source_type="description",
            original_text=text,
        )
    
    def _extract_goal(self, text: str) -> str:
        """Extract primary goal from text"""
        # First line is often the goal
        lines = text.strip().split("\n")
        goal = lines[0].strip()
        
        # If first line is too long, find a better goal
        if len(goal) > 200:
            # Look for imperative sentences
            sentences = re.split(r'[.!?]\s+', text)
            for sent in sentences:
                sent_clean = sent.strip()
                if sent_clean and len(sent_clean) < 150:
                    goal = sent_clean
                    break
        
        return goal or "Generate code"
    
    def _extract_section(self, text: str, keywords: list[str]) -> Optional[str]:
        """Extract a section from text by keywords"""
        text_lower = text.lower()
        
        for keyword in keywords:
            pattern = rf"{re.escape(keyword)}[:\s]*([^\n]*(?:\n(?![a-z]+:)[^\n]*)*)"
            match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            if match:
                content = text[match.start(1):match.end(1)].strip()
                if content:
                    return content
        
        return None
    
    def _extract_constraints(self, text: str) -> list[str]:
        """Extract constraints from text"""
        constraints = []
        
        # Look for constraint sections
        constraint_patterns = [
            r"constraints?:\s*\n((?:[-•*].*\n?)+)",
            r"must:\s*(.*?)(?:\n|$)",
            r"should:\s*(.*?)(?:\n|$)",
        ]
        
        for pattern in constraint_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                items = match.group(1).strip().split("\n")
                for item in items:
                    item_clean = re.sub(r"^[-•*]\s*", "", item).strip()
                    if item_clean:
                        constraints.append(item_clean)
        
        return list(set(constraints))  # Remove duplicates
    
    def _extract_examples(self, text: str) -> list[str]:
        """Extract examples from text"""
        examples = []
        
        # Look for example sections
        pattern = r"example[s]?[:\s]*\n((?:```.*?```|[^\n]*(?:\n(?![a-z]+:)[^\n]*)*)?)"
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            example = match.group(1).strip()
            if example:
                examples.append(example)
        
        return examples
