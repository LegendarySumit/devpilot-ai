"""
Debug Formatter - Formats processing result into DebugResponse
"""
from typing import Dict, Any, List
from .debug_models import (
    DebugResponse,
    AnalysisMetadata,
    RootCauseAnalysis,
    Solution,
    LearningContent,
)
from .. import processing_framework


class DebugFormatter(processing_framework.Formatter):
    """Formats debug processing results into structured DebugResponse"""
    
    stage_name = "debug_formatter"
    
    def format(self, data: Dict[str, Any]) -> processing_framework.EngineResponse:
        """Format processing result into DebugResponse"""
        
        analysis = data.get("analysis", {})
        processing = data.get("processing", {})
        
        # Create analysis metadata
        analysis_metadata = AnalysisMetadata(
            artifact_type=analysis.get("artifact_type", "error"),
            language=analysis.get("language", "unknown"),
            framework=analysis.get("framework"),
            category=analysis.get("category", "unknown"),
            severity=analysis.get("severity", "medium"),
            confidence=analysis.get("confidence", 0.5),
            stack_trace_present=analysis.get("stack_trace_present", False),
        )
        # Create root cause analysis
        root_cause_obj = RootCauseAnalysis(
            summary=processing.get("summary", "Error detected"),
            root_cause=processing.get("root_cause", "Unknown"),
            why_it_happened=processing.get("why_it_happened", ""),
            confidence=analysis.get("confidence", 0.7),
        )
        
        # Create solution
        solution = Solution(
            steps=processing.get("solution_steps", []),
            corrected_code=processing.get("example_code", ""),
            dependencies_to_add=processing.get("dependencies_to_add", []),
            commands_to_run=self._extract_commands(processing.get("solution_steps", [])),
        )
        
        # Create learning content (optional)
        learning = None
        if data.get("learning_mode"):
            learning_data = processing.get("learning", {})
            learning = LearningContent(
                concept_explained=learning_data.get("concept", ""),
                common_mistakes=self._generate_common_mistakes(analysis.get("language")),
                prevention_strategies=processing.get("prevention_tips", []),
                best_practices=self._generate_best_practices(analysis.get("language")),
            )
        
        # Create response
        response = DebugResponse(
            analysis=analysis_metadata,
            diagnosis=root_cause_obj,
            solution=solution,
            learning=learning,
            resources=self._generate_resources(analysis.get("language"), analysis.get("framework")),
            next_actions=self._generate_next_actions(analysis.get("severity")),
            confidence_score=analysis.get("confidence", 0.5),
            learning_mode=data.get("learning_mode", False),
        )
        
        return response
    
    def _extract_commands(self, steps: List[str]) -> List[str]:
        """Extract executable commands from solution steps"""
        commands = []
        
        for step in steps:
            # Extract commands like "pip install ..." or "npm install ..."
            if any(cmd in step for cmd in ["pip ", "npm ", "yarn ", "docker ", "git "]):
                # Clean up the command
                cmd = step.replace("Run: ", "").strip()
                if cmd:
                    commands.append(cmd)
        
        return commands
    
    def _generate_common_mistakes(self, language: str) -> List[str]:
        """Generate common mistakes for language"""
        
        mistakes = {
            "python": [
                "Forgetting to install dependencies",
                "Mixing indentation (tabs vs spaces)",
                "Using undefined variables",
                "Incorrect method names on objects",
            ],
            "javascript": [
                "Not installing npm packages",
                "Async/await confusion",
                "Undefined references",
                "Type coercion issues",
            ],
            "sql": [
                "Misspelled column/table names",
                "Missing WHERE clause",
                "Incorrect JOIN conditions",
                "Data type mismatches",
            ],
        }
        
        return mistakes.get(language, [
            "Not reading error messages carefully",
            "Wrong variable types",
            "Missing dependencies",
        ])
    
    def _generate_best_practices(self, language: str) -> List[str]:
        """Generate best practices for language"""
        
        practices = {
            "python": [
                "Use virtual environments for isolation",
                "Add type hints for clarity",
                "Use logging instead of print()",
                "Write unit tests for your code",
            ],
            "javascript": [
                "Use const/let instead of var",
                "Implement proper error handling",
                "Use async/await for asynchronous code",
                "Lint your code with ESLint",
            ],
            "sql": [
                "Always use parameterized queries",
                "Add proper indexes for performance",
                "Use meaningful column names",
                "Include constraints and validations",
            ],
        }
        
        return practices.get(language, [
            "Test thoroughly",
            "Read documentation",
            "Keep code simple and clear",
        ])
    
    def _generate_resources(self, language: str, framework: str) -> List[str]:
        """Generate relevant documentation links"""
        
        resources = []
        
        # Language resources
        if language == "python":
            resources.append("https://docs.python.org/3/")
            if framework == "fastapi":
                resources.append("https://fastapi.tiangolo.com/")
            elif framework == "django":
                resources.append("https://docs.djangoproject.com/")
        
        elif language == "javascript":
            resources.append("https://developer.mozilla.org/en-US/docs/Web/JavaScript/")
            if framework == "react":
                resources.append("https://react.dev/")
            elif framework == "express":
                resources.append("https://expressjs.com/")
        
        elif language == "sql":
            resources.append("https://www.postgresql.org/docs/")
            resources.append("https://dev.mysql.com/doc/")
        
        return resources
    
    def _generate_next_actions(self, severity: str) -> List[str]:
        """Generate next actions based on severity"""
        
        actions = [
            "Review the solution steps above",
            "Test your fix with different inputs",
        ]
        
        if severity == "critical":
            actions.insert(0, "Implement fix immediately")
            actions.append("Monitor logs for recurrence")
        elif severity == "high":
            actions.append("Prioritize fixing this issue")
        
        actions.append("Add a test case to prevent regression")
        actions.append("Document the issue and solution")
        
        return actions
