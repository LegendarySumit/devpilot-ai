"""
Debug Input Adapter - Normalizes error/log input to DebugArtifact
"""
from typing import Dict, Any, Optional, Union
from .debug_models import DebugArtifact, RelatedArtifact, MultiArtifactDebugInput
from .. import processing_framework


class DebugInputAdapter(processing_framework.InputAdapter):
    """Converts raw error/log input to canonical DebugArtifact"""
    
    stage_name = "debug_input_adapter"
    
    def adapt(self, raw_input: Dict[str, Any] | str) -> DebugArtifact:
        """Parse raw error/log to DebugArtifact (single artifact)"""
        
        if isinstance(raw_input, str):
            return self._parse_raw_error(raw_input)
        
        if isinstance(raw_input, dict):
            return DebugArtifact(
                content=raw_input.get("content", raw_input.get("error", "")),
                language_hint=raw_input.get("language_hint"),
                framework_hint=raw_input.get("framework_hint"),
                context=raw_input.get("context"),
                artifact_type=raw_input.get("artifact_type", "error"),
                original_input=raw_input,
            )
        
        return self._parse_raw_error(str(raw_input))
    
    def adapt_multi(self, raw_input: Dict[str, Any]) -> Union[DebugArtifact, MultiArtifactDebugInput]:
        """Parse raw input to support both single and multi-artifact"""
        
        # Check if this is a multi-artifact input
        if "primary_artifact" in raw_input and "related_artifacts" in raw_input:
            return self._parse_multi_artifact(raw_input)
        
        # Fall back to single artifact
        return self.adapt(raw_input)
    
    def _parse_multi_artifact(self, raw_input: Dict[str, Any]) -> MultiArtifactDebugInput:
        """Parse multiple artifacts together"""
        
        # Parse primary artifact
        primary = raw_input.get("primary_artifact", {})
        if isinstance(primary, dict):
            primary_artifact = DebugArtifact(
                content=primary.get("content", primary.get("error", "")),
                language_hint=primary.get("language_hint"),
                framework_hint=primary.get("framework_hint"),
                context=primary.get("context"),
                artifact_type=primary.get("artifact_type", "error"),
                original_input=primary,
            )
        else:
            primary_artifact = primary
        
        # Parse related artifacts
        related = []
        for artifact_data in raw_input.get("related_artifacts", []):
            if isinstance(artifact_data, dict):
                artifact_type = artifact_data.get("artifact_type", "code")
                related_artifact = RelatedArtifact(
                    artifact_type=artifact_type,
                    filename=artifact_data.get("filename"),
                    language=artifact_data.get("language"),
                    content=artifact_data.get("content", ""),
                    description=artifact_data.get("description"),
                )
                related.append(related_artifact)
        
        return MultiArtifactDebugInput(
            primary_artifact=primary_artifact,
            related_artifacts=related,
        )
    
    def _parse_raw_error(self, text: str) -> DebugArtifact:
        """Parse raw error/log text"""
        
        text = text.strip()
        
        # Detect language/framework from content
        language = self._detect_language(text)
        framework = self._detect_framework(text)
        artifact_type = self._detect_artifact_type(text)
        
        return DebugArtifact(
            content=text,
            language_hint=language,
            framework_hint=framework,
            artifact_type=artifact_type,
            original_input={"raw_input": text},
        )
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect programming language from error content"""
        
        text_lower = text.lower()
        
        # Python indicators (check first - more specific)
        if any(pattern in text_lower for pattern in [
            "traceback",
            "python",
            "modulenotfounderror",
            "importerror",
            "keyerror",
            "indentation",
            "typeerror",
            "valueerror",
            "attributeerror",
        ]):
            return "python"
        
        # JavaScript/Node indicators
        if any(pattern in text_lower for pattern in [
            "cannot find module",
            "at node",
            "at async",
            "referenceerror",
            "nodejs",
            "npm",
        ]):
            return "javascript"
        
        # Java indicators
        if any(pattern in text_lower for pattern in [
            "exception",
            "java.",
            "at java.",
            "caused by",
        ]):
            return "java"
        
        # SQL indicators
        if any(pattern in text_lower for pattern in [
            "sql",
            "select",
            "from",
            "where",
            "syntax error",
        ]):
            return "sql"
        
        # Go indicators
        if any(pattern in text_lower for pattern in [
            "panic",
            "goroutine",
            "main.go",
        ]):
            return "go"
        
        return None
    
    def _detect_framework(self, text: str) -> Optional[str]:
        """Detect framework from error content"""
        
        text_lower = text.lower()
        
        # Python frameworks
        frameworks = {
            "fastapi": ["fastapi", "starlette"],
            "django": ["django", "django."],
            "flask": ["flask", "werkzeug"],
            "sqlalchemy": ["sqlalchemy", "integrity error"],
            "pytest": ["pytest", "assert"],
        }
        
        # JavaScript frameworks
        frameworks.update({
            "react": ["react", "jsx"],
            "nextjs": ["next.js", "_next"],
            "express": ["express", "middleware"],
            "nodejs": ["node", "npm"],
        })
        
        # Java frameworks
        frameworks.update({
            "spring": ["spring", "springframework"],
            "maven": ["maven", "pom.xml"],
        })
        
        # SQL/DB
        frameworks.update({
            "postgres": ["postgres", "psycopg"],
            "mysql": ["mysql", "mysqldump"],
            "mongodb": ["mongodb", "mongo"],
        })
        
        for framework, keywords in frameworks.items():
            if any(kw in text_lower for kw in keywords):
                return framework
        
        return None
    
    def _detect_artifact_type(self, text: str) -> str:
        """Detect artifact type from content"""
        
        text_lower = text.lower()
        
        if "traceback" in text_lower:
            return "python_traceback"
        elif "exception" in text_lower or "error:" in text_lower:
            return "exception"
        elif any(s in text_lower for s in ["select", "from", "where", "insert", "update"]):
            return "sql_error"
        elif "error:" in text_lower and ("response" in text_lower or "status" in text_lower):
            return "http_error"
        elif "docker" in text_lower or "container" in text_lower:
            return "docker_log"
        elif "kubernetes" in text_lower or "k8s" in text_lower or "pod" in text_lower:
            return "kubernetes_log"
        elif "merge conflict" in text_lower:
            return "git_conflict"
        elif "build" in text_lower and ("error" in text_lower or "failed" in text_lower):
            return "build_error"
        else:
            return "error"
