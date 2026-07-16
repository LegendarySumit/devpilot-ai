"""
Debug Strategy Engine - Selects analysis strategy based on error type
Completely ported from old implementation (was MISSING in new code)
"""
from typing import Dict, Any, List


class DebugStrategy:
    """Represents a debugging strategy for a specific error type"""
    
    def __init__(
        self,
        strategy_type: str,
        focus_areas: List[str],
        recommended_checks: List[str],
        likely_causes: List[str],
        documentation_sections: List[str],
    ):
        self.strategy_type = strategy_type
        self.focus_areas = focus_areas
        self.recommended_checks = recommended_checks
        self.likely_causes = likely_causes
        self.documentation_sections = documentation_sections
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_type": self.strategy_type,
            "focus_areas": self.focus_areas,
            "recommended_checks": self.recommended_checks,
            "likely_causes": self.likely_causes,
            "documentation_sections": self.documentation_sections,
        }


class DebugStrategyEngine:
    """
    Selects analysis strategy based on error type.
    
    Strategies:
    - Python: import_error, type_error, syntax_error
    - JavaScript: type_error, import_error
    - Java: general strategy
    - SQL: general strategy
    - Docker/Kubernetes: general strategy
    - Generic: fallback
    """
    
    def get_strategy(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get appropriate strategy for this error"""
        
        language = metadata.get("language", "unknown")
        
        if language == "python":
            return self._python_strategy(metadata).to_dict()
        elif language in ["javascript", "typescript"]:
            return self._javascript_strategy(metadata).to_dict()
        elif language == "java":
            return self._java_strategy(metadata).to_dict()
        elif language == "sql":
            return self._sql_strategy(metadata).to_dict()
        elif metadata.get("framework") in ["docker", "kubernetes"]:
            return self._docker_kubernetes_strategy(metadata).to_dict()
        else:
            return self._generic_strategy(metadata).to_dict()
    
    def _python_strategy(self, metadata: Dict[str, Any]) -> DebugStrategy:
        """Strategy for Python errors"""
        
        category = metadata.get("category", "unknown")  # Used in if statements below
        
        if category == "import_error":
            return DebugStrategy(
                strategy_type="python_import",
                focus_areas=[
                    "Module availability",
                    "Virtual environment",
                    "Installation status",
                    "Python path",
                ],
                recommended_checks=[
                    "Is the module installed? (pip list)",
                    "Are you in the correct virtual environment?",
                    "Does the import statement match the module name?",
                    "Is there a circular import?",
                ],
                likely_causes=[
                    "Module not installed",
                    "Wrong virtual environment",
                    "Typo in import statement",
                    "Circular import dependency",
                    "Module version incompatibility",
                ],
                documentation_sections=[
                    "Python modules and packages",
                    "Virtual environments",
                    "Package management with pip",
                ],
            )
        
        if category == "type_error":
            return DebugStrategy(
                strategy_type="python_type",
                focus_areas=[
                    "Type mismatches",
                    "None handling",
                    "Function signatures",
                ],
                recommended_checks=[
                    "What type does the variable actually have?",
                    "Is a None value being used where it shouldn't be?",
                    "Do function arguments match the expected types?",
                ],
                likely_causes=[
                    "Passing wrong type to function",
                    "NoneType when expecting different type",
                    "Type mismatch in operation",
                    "Missing type conversion",
                ],
                documentation_sections=["Python types", "Type hints"],
            )
        
        if category == "syntax_error":
            return DebugStrategy(
                strategy_type="python_syntax",
                focus_areas=[
                    "Indentation",
                    "Syntax rules",
                    "Missing colons/brackets",
                ],
                recommended_checks=[
                    "Check indentation levels",
                    "Are all brackets/parentheses closed?",
                    "Are all lines ending correctly?",
                    "Is the syntax valid for this Python version?",
                ],
                likely_causes=[
                    "Incorrect indentation",
                    "Missing colon",
                    "Unclosed bracket/parenthesis",
                    "Using wrong Python version syntax",
                ],
                documentation_sections=["Python syntax", "Indentation"],
            )
        
        return self._generic_strategy(metadata)
    
    def _javascript_strategy(self, metadata: Dict[str, Any]) -> DebugStrategy:
        """Strategy for JavaScript/TypeScript errors"""
        
        category = metadata.get("category", "unknown")
        
        if category == "type_error":
            return DebugStrategy(
                strategy_type="js_type",
                focus_areas=[
                    "Type coercion",
                    "Undefined values",
                    "Method availability",
                ],
                recommended_checks=[
                    "What type is the variable?",
                    "Is the method available on this object?",
                    "Is the value undefined or null?",
                ],
                likely_causes=[
                    "Calling method on undefined",
                    "Type misunderstanding",
                    "Async/await timing issue",
                    "Module import issue",
                ],
                documentation_sections=[
                    "JavaScript types",
                    "Async/await",
                    "Module system",
                ],
            )
        
        if category == "import_error":
            return DebugStrategy(
                strategy_type="js_import",
                focus_areas=[
                    "Module resolution",
                    "File paths",
                    "Package installation",
                ],
                recommended_checks=[
                    "Is the module installed?",
                    "Is the import path correct?",
                    "Are you using the right import syntax?",
                ],
                likely_causes=[
                    "Module not installed",
                    "Wrong import path",
                    "CommonJS vs ES modules mismatch",
                    "Package.json misconfiguration",
                ],
                documentation_sections=[
                    "Module systems",
                    "Package management",
                ],
            )
        
        return self._generic_strategy(metadata)
    
    def _java_strategy(self, metadata: Dict[str, Any]) -> DebugStrategy:
        """Strategy for Java errors"""
        
        return DebugStrategy(
            strategy_type="java_general",
            focus_areas=[
                "Classpath",
                "Type casting",
                "Null pointers",
                "Memory",
            ],
            recommended_checks=[
                "Is the required library in the classpath?",
                "Are all classes properly imported?",
                "Could a null reference cause this?",
                "Is there enough heap memory?",
            ],
            likely_causes=[
                "Missing dependency",
                "Incorrect classpath",
                "Null pointer dereference",
                "Type casting error",
                "Memory exhaustion",
            ],
            documentation_sections=[
                "Java classpath",
                "Exception handling",
            ],
        )
    
    def _sql_strategy(self, metadata: Dict[str, Any]) -> DebugStrategy:
        """Strategy for SQL errors"""
        
        return DebugStrategy(
            strategy_type="sql_general",
            focus_areas=[
                "Query syntax",
                "Schema",
                "Constraints",
                "Data types",
            ],
            recommended_checks=[
                "Is the SQL syntax correct?",
                "Do all referenced tables/columns exist?",
                "Are all constraints satisfied?",
                "Are the data types compatible?",
            ],
            likely_causes=[
                "Syntax error in query",
                "Missing table or column",
                "Constraint violation",
                "Type mismatch",
                "Join condition error",
            ],
            documentation_sections=[
                "SQL syntax",
                "Database constraints",
                "Query optimization",
            ],
        )
    
    def _docker_kubernetes_strategy(self, metadata: Dict[str, Any]) -> DebugStrategy:
        """Strategy for Docker/Kubernetes errors"""
        
        return DebugStrategy(
            strategy_type="container_deployment",
            focus_areas=[
                "Image building",
                "Port mapping",
                "Volume mounting",
                "Network configuration",
            ],
            recommended_checks=[
                "Does the Dockerfile have valid syntax?",
                "Are all required ports exposed?",
                "Are volumes mounted correctly?",
                "Is the network configuration correct?",
            ],
            likely_causes=[
                "Invalid Dockerfile syntax",
                "Port conflicts",
                "Missing volumes",
                "Network isolation",
                "Image not found",
            ],
            documentation_sections=[
                "Dockerfile best practices",
                "Docker networking",
                "Kubernetes manifests",
            ],
        )
    
    def _generic_strategy(self, metadata: Dict[str, Any]) -> DebugStrategy:
        """Generic strategy for unknown error types"""
        
        return DebugStrategy(
            strategy_type="generic",
            focus_areas=[
                "Error message analysis",
                "Stack trace examination",
                "Context reconstruction",
            ],
            recommended_checks=[
                "What does the exact error message say?",
                "What was the last successful operation?",
                "What changed before the error appeared?",
                "Is there a stack trace?",
            ],
            likely_causes=[
                "Configuration issue",
                "Missing dependency",
                "Version incompatibility",
                "Environment issue",
            ],
            documentation_sections=[
                "Error handling",
                "Debugging techniques",
            ],
        )
