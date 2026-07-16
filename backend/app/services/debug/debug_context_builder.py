"""
Debug Context Builder - Enriches error artifacts with additional context
Completely ported from old implementation (was MISSING in new code)
"""
import re
from typing import List, Optional, Dict, Any


class DebugContextBuilder:
    """
    Enriches error artifacts with additional context.
    
    Extracts:
    - Related imports/requires
    - Framework version
    - Related configuration files
    - Similar errors for reference
    - Relevant documentation links
    """
    
    def build_context(
        self, 
        metadata: Dict[str, Any], 
        content: str,
    ) -> Dict[str, Any]:
        """Build enriched context for the error"""
        
        language = metadata.get("language", "unknown")
        framework = metadata.get("framework")
        category = metadata.get("category", "unknown")
        
        context = {
            "related_imports": self._extract_imports(content, language),
            "framework_version": self._detect_framework_version(content, framework),
            "related_configs": self._extract_related_configs(language),
            "similar_errors": self._get_similar_errors(category, language),
            "documentation_links": self._get_documentation_links(metadata),
        }
        
        return context
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract relevant imports/requires from content"""
        
        imports = []
        
        if language == "python":
            matches = re.findall(r'(?:from|import)\s+([a-zA-Z0-9._]+)', content)
            imports = list(set(matches))[:5]
        
        elif language in ["javascript", "typescript"]:
            matches = re.findall(r'(?:import|require)\s+[\'"]([a-zA-Z0-9._/-]+)[\'"]', content)
            imports = list(set(matches))[:5]
        
        elif language == "java":
            matches = re.findall(r'import\s+([a-zA-Z0-9.]+)', content)
            imports = list(set(matches))[:5]
        
        return imports
    
    def _detect_framework_version(self, content: str, framework: Optional[str]) -> Optional[str]:
        """Detect framework version if mentioned"""
        
        if not framework:
            return None
        
        version_patterns = {
            "fastapi": r"fastapi[=\s]*([0-9.]+)",
            "django": r"django[=\s]*([0-9.]+)",
            "flask": r"flask[=\s]*([0-9.]+)",
            "react": r"react[=\s]*([0-9.]+)",
            "express": r"express[=\s]*([0-9.]+)",
            "sqlalchemy": r"sqlalchemy[=\s]*([0-9.]+)",
        }
        
        pattern = version_patterns.get(framework.lower())
        if pattern:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_related_configs(self, language: str) -> List[str]:
        """Extract configuration files that might be relevant"""
        
        configs = []
        
        if language == "python":
            configs = ["requirements.txt", "setup.py", "pyproject.toml", ".env", "manage.py"]
        elif language in ["javascript", "typescript"]:
            configs = ["package.json", ".env", "tsconfig.json", "webpack.config.js"]
        elif language == "java":
            configs = ["pom.xml", "build.gradle", "application.properties", ".env"]
        elif language in ["docker", "kubernetes"]:
            configs = ["Dockerfile", "docker-compose.yml", "deployment.yaml", "service.yaml"]
        
        return configs
    
    def _get_similar_errors(self, category: str, language: str) -> List[str]:
        """Get common similar errors for this category"""
        
        if category == "import_error":
            return [
                "ModuleNotFoundError: No module named",
                "ImportError: cannot import name",
                "Cannot find module",
                "No module named",
            ]
        
        if category == "type_error":
            return [
                "TypeError: unsupported operand type(s)",
                "TypeError: 'NoneType' object is not",
                "TypeError: expected str, bytes or os.PathLike object",
            ]
        
        if category == "syntax_error":
            return [
                "SyntaxError: invalid syntax",
                "SyntaxError: unexpected EOF",
                "Unexpected token",
            ]
        
        if category == "validation_error":
            return [
                "ValidationError: value error, required",
                "Schema validation failed",
                "Validation error: missing required",
            ]
        
        if category == "database_error":
            return [
                "IntegrityError: duplicate key",
                "OperationalError: no such table",
                "Foreign key constraint fails",
            ]
        
        if category == "authentication_error":
            return [
                "PermissionError: access denied",
                "AuthenticationError: invalid credentials",
                "Unauthorized: missing authentication",
            ]
        
        if category == "network_error":
            return [
                "ConnectionError: refused connection",
                "TimeoutError: operation timed out",
                "ConnectionRefusedError: [Errno 111]",
            ]
        
        return []
    
    def _get_documentation_links(self, metadata: Dict[str, Any]) -> List[str]:
        """Get relevant documentation links"""
        
        links = []
        framework = metadata.get("framework")
        language = metadata.get("language", "unknown")
        category = metadata.get("category", "unknown")
        error_message = metadata.get("error_message", "")
        
        if framework == "fastapi":
            if category == "validation_error":
                links.append("https://fastapi.tiangolo.com/tutorial/body/")
            if category == "type_error":
                links.append("https://fastapi.tiangolo.com/python-types/")
        
        if framework == "django":
            if category == "database_error":
                links.append("https://docs.djangoproject.com/en/stable/topics/db/models/")
            if category == "authentication_error":
                links.append("https://docs.djangoproject.com/en/stable/topics/auth/")
        
        if language == "python":
            if category == "import_error":
                links.append("https://docs.python.org/3/tutorial/modules.html")
            if category == "type_error":
                links.append("https://docs.python.org/3/library/stdtypes.html")
        
        if language == "javascript":
            if category == "type_error":
                links.append("https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypeError")
        
        if category == "syntax_error" and error_message:
            links.append(f"https://www.google.com/search?q={error_message}")
        
        return links[:3]
