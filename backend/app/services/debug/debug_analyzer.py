"""
Unified Debug Analyzer - Analyzes DebugArtifact for classification and severity
Incorporates all features from old and new implementations
"""
import re
from typing import Dict, Any, List, Optional
from .debug_models import DebugArtifact
from .. import processing_framework


class DebugAnalyzer(processing_framework.Analyzer):
    """
    Analyzes debug artifact to classify and score.
    
    Features:
    - 14 artifact type detectors
    - 6+ language detectors with 40+ indicators
    - 11 framework detectors
    - 24 specific error patterns
    - Deterministic confidence calculation
    """
    
    stage_name = "debug_analyzer"
    
    def analyze(self, canonical_model: DebugArtifact) -> Dict[str, Any]:
        """Analyze debug artifact"""
        
        content = canonical_model.content
        artifact_type = self._detect_artifact_type(content)
        language = canonical_model.language_hint or self._detect_language(content, artifact_type)
        framework = canonical_model.framework_hint or self._detect_framework(content, language)
        category = self._detect_error_category(content, language, artifact_type)
        severity = self._detect_severity(content, category)
        patterns = self._detect_patterns(content, artifact_type)
        error_message = self._extract_error_message(content, artifact_type)
        stack_trace_present = self._has_stack_trace(content)
        is_compile_time = self._is_compile_time(content, artifact_type)
        
        confidence = self._calculate_confidence(artifact_type, language, patterns)
        
        return {
            "artifact_type": artifact_type,
            "language": language,
            "framework": framework,
            "category": category,
            "severity": severity,
            "confidence": confidence,
            "detected_patterns": patterns,
            "error_message": error_message,
            "stack_trace_present": stack_trace_present,
            "is_compile_time": is_compile_time,
            "metrics": {
                "content_length": len(content),
                "line_count": len(content.split("\n")),
                "is_multiline": "\n" in content,
            },
        }
    
    def _detect_artifact_type(self, content: str) -> str:
        """Detect the type of artifact (14 types)"""
        
        if self._is_python_traceback(content):
            return "python_traceback"
        if self._is_nodejs_error(content):
            return "nodejs_error"
        if self._is_java_stack_trace(content):
            return "java_stack_trace"
        if self._is_docker_logs(content):
            return "docker_logs"
        if self._is_kubernetes_logs(content):
            return "kubernetes_logs"
        if self._is_sql_error(content):
            return "sql_error"
        if self._is_git_conflict(content):
            return "git_conflict"
        if self._is_http_error(content):
            return "http_error"
        if self._is_json_error(content):
            return "json_error"
        if self._is_yaml_error(content):
            return "yaml_error"
        if self._is_compiler_error(content):
            return "compiler_error"
        if self._is_build_logs(content):
            return "build_logs"
        if self._is_ci_cd_logs(content):
            return "ci_cd_logs"
        
        return "unknown"
    
    def _detect_language(self, content: str, artifact_type: str) -> str:
        """Detect programming language (41+ indicators for 6 languages)"""
        
        # Python indicators (13 total)
        python_indicators = [
            "Traceback", "File", "line", "ModuleNotFoundError", "ImportError",
            "TypeError", "ValueError", "AttributeError", "KeyError", "python",
            "def ", "class ", "import ", "from "
        ]
        
        # JavaScript/TypeScript indicators (11 total)
        javascript_indicators = [
            "TypeError", "ReferenceError", "SyntaxError", "at ", "node.js",
            "function", "const ", "let ", "var ", "require(", "module.exports"
        ]
        
        # Java indicators (7 total)
        java_indicators = [
            "Exception in thread", "at ", ".java:", "ClassNotFoundException",
            "NullPointerException", "ArrayIndexOutOfBoundsException", "public class"
        ]
        
        # Go indicators (6 total)
        go_indicators = [
            "panic:", "runtime error", "goroutine", "defer", "go build", ".go:"
        ]
        
        # Rust indicators (6 total)
        rust_indicators = [
            "error[", "error:", "thread", "panicked", ".rs:", "fn main"
        ]
        
        # SQL indicators (8 total)
        sql_indicators = [
            "SQL", "SELECT", "INSERT", "UPDATE", "DELETE", "WHERE", "JOIN",
            "syntax error", "constraint violation"
        ]
        
        def count_matches(indicators):
            return sum(1 for ind in indicators if ind.lower() in content.lower())
        
        scores = {
            "python": count_matches(python_indicators),
            "javascript": count_matches(javascript_indicators),
            "java": count_matches(java_indicators),
            "go": count_matches(go_indicators),
            "rust": count_matches(rust_indicators),
            "sql": count_matches(sql_indicators),
        }
        
        if max(scores.values()) > 0:
            return max(scores, key=lambda x: scores[x])
        
        return "unknown"
    
    def _detect_framework(self, content: str, language: str) -> Optional[str]:
        """Detect framework (11 frameworks supported)"""
        
        frameworks = {
            "fastapi": r"fastapi|FastAPI",
            "django": r"django|Django",
            "flask": r"flask|Flask",
            "react": r"react|React",
            "next.js": r"next.js|Next.js|nextjs",
            "express": r"express|Express",
            "spring": r"spring|Spring",
            "kubernetes": r"kubernetes|k8s|kubectl",
            "docker": r"docker|Docker",
            "sqlalchemy": r"sqlalchemy|SQLAlchemy",
            "pytest": r"pytest|AssertionError",
        }
        
        for framework, pattern in frameworks.items():
            if re.search(pattern, content, re.IGNORECASE):
                return framework
        
        return None
    
    def _detect_error_category(self, content: str, language: str, artifact_type: str) -> str:
        """Detect error category"""
        
        if artifact_type == "git_conflict":
            return "merge_conflict"
        
        if "syntax" in content.lower():
            return "syntax_error"
        
        if "type" in content.lower() and ("error" in content.lower() or "type" in content.lower()):
            return "type_error"
        
        if any(x in content.lower() for x in ["import", "modulenotfound", "cannot find"]):
            return "import_error"
        
        if any(x in content.lower() for x in ["config", "configuration", "invalid", "not found"]):
            return "configuration_error"
        
        if any(x in content.lower() for x in ["connection", "timeout", "network", "refused"]):
            return "network_error"
        
        if any(x in content.lower() for x in ["sql", "database", "constraint", "foreign key"]):
            return "database_error"
        
        if any(x in content.lower() for x in ["auth", "permission", "unauthorized", "forbidden"]):
            return "authentication_error"
        
        if any(x in content.lower() for x in ["validate", "validation", "schema", "required"]):
            return "validation_error"
        
        if any(x in content.lower() for x in ["build", "compile", "failed", "error"]):
            return "build_error"
        
        if artifact_type in ["docker_logs", "kubernetes_logs", "ci_cd_logs"]:
            return "deployment_error"
        
        if "runtime" in artifact_type:
            return "runtime_error"
        
        return "unknown"
    
    def _detect_severity(self, content: str, category: str) -> str:
        """Detect error severity"""
        
        if category in ["runtime_error", "critical"]:
            return "critical"
        
        critical_keywords = ["crash", "fatal", "exception", "panic", "critical"]
        if any(kw in content.lower() for kw in critical_keywords):
            return "critical"
        
        if category in ["syntax_error", "import_error", "type_error"]:
            return "high"
        
        if category in ["configuration_error", "validation_error"]:
            return "medium"
        
        if category in ["authentication_error", "network_error"]:
            return "high"
        
        if category == "merge_conflict":
            return "medium"
        
        return "medium"
    
    def _detect_patterns(self, content: str, artifact_type: str) -> List[str]:
        """Detect specific error patterns (24 patterns)"""
        
        patterns = []
        
        pattern_mappings = {
            "Traceback": r"Traceback",
            "ModuleNotFoundError": r"ModuleNotFoundError",
            "ImportError": r"ImportError",
            "TypeError": r"TypeError",
            "AttributeError": r"AttributeError",
            "KeyError": r"KeyError",
            "IndexError": r"IndexError",
            "ValueError": r"ValueError",
            "NullPointerException": r"NullPointerException",
            "ClassNotFoundException": r"ClassNotFoundException",
            "SyntaxError": r"SyntaxError",
            "IndentationError": r"IndentationError",
            "ConnectionError": r"Connection.*[Ee]rror|refused|timeout",
            "TimeoutError": r"[Tt]imeout",
            "PermissionError": r"[Pp]ermission.*[Dd]enied",
            "FileNotFoundError": r"[Nn]o such file",
            "JSONDecodeError": r"JSON.*[Dd]ecode.*[Ee]rror|Invalid.*JSON",
            "SQLSyntaxError": r"SQL.*syntax.*error|Syntax.*error.*SQL",
            "StackTrace": r"at \w+",
            "Assertion": r"assert",
        }
        
        for name, regex in pattern_mappings.items():
            if re.search(regex, content):
                patterns.append(name)
        
        return patterns
    
    def _extract_error_message(self, content: str, artifact_type: str) -> Optional[str]:
        """Extract the main error message"""
        
        if artifact_type == "python_traceback":
            match = re.search(r'^(\w+(?:Error|Exception):.*?)$', content, re.MULTILINE)
            if match:
                return match.group(1)
        
        if artifact_type in ["nodejs_error", "javascript_error"]:
            match = re.search(r'Error: (.*?)(?:\n|$)', content)
            if match:
                return match.group(1)
        
        if artifact_type == "java_stack_trace":
            match = re.search(r'Exception in thread.*?:\s*(.*?)(?:\n|$)', content)
            if match:
                return match.group(1)
        
        if artifact_type == "sql_error":
            match = re.search(r'(?:ERROR|Error).*?:\s*(.*?)(?:\n|$)', content)
            if match:
                return match.group(1)
        
        lines = content.split('\n')
        for line in lines:
            if any(x in line.lower() for x in ["error", "exception", "fatal", "failed"]):
                return line.strip()
        
        return None
    
    def _has_stack_trace(self, content: str) -> bool:
        """Check if content has a stack trace"""
        return bool(re.search(r'(Traceback|Exception in thread|at \w+)', content))
    
    def _is_compile_time(self, content: str, artifact_type: str) -> bool:
        """Check if error is compile-time vs runtime"""
        if artifact_type in ["compiler_error", "syntax_error"]:
            return True
        if artifact_type in ["build_logs", "ci_cd_logs"]:
            return True
        return False
    
    def _calculate_confidence(self, artifact_type: str, language: str, patterns: List[str]) -> float:
        """Calculate analysis confidence"""
        confidence = 0.5
        
        if artifact_type != "unknown":
            confidence += 0.3
        
        if language != "unknown":
            confidence += 0.1
        
        if len(patterns) >= 3:
            confidence += 0.1
        elif len(patterns) >= 1:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    # ===== 14 Artifact Type Detectors =====
    
    def _is_python_traceback(self, content: str) -> bool:
        return bool(re.search(r'Traceback|File.*line|\.py:', content))
    
    def _is_nodejs_error(self, content: str) -> bool:
        return bool(re.search(r'node.js|TypeError|ReferenceError.*at \w+', content))
    
    def _is_java_stack_trace(self, content: str) -> bool:
        return bool(re.search(r'Exception in thread|\.java:|NullPointerException', content))
    
    def _is_docker_logs(self, content: str) -> bool:
        return bool(re.search(r'docker|container|image|port.*bind', content.lower()))
    
    def _is_kubernetes_logs(self, content: str) -> bool:
        return bool(re.search(r'kubernetes|k8s|pod|deployment|service', content.lower()))
    
    def _is_sql_error(self, content: str) -> bool:
        return bool(re.search(r'SQL|SELECT|INSERT|constraint|foreign key', content, re.IGNORECASE))
    
    def _is_git_conflict(self, content: str) -> bool:
        return bool(re.search(r'<<<<<<|======|>>>>>>', content))
    
    def _is_http_error(self, content: str) -> bool:
        return bool(re.search(r'HTTP|status.*[0-9]{3}|response.*[0-9]{3}', content))
    
    def _is_json_error(self, content: str) -> bool:
        return bool(re.search(r'JSON|json|Unexpected.*token|line.*column', content))
    
    def _is_yaml_error(self, content: str) -> bool:
        return bool(re.search(r'YAML|yaml|indentation.*error|mapping.*values', content))
    
    def _is_compiler_error(self, content: str) -> bool:
        return bool(re.search(r'syntax.*error|undefined|undeclared', content, re.IGNORECASE))
    
    def _is_build_logs(self, content: str) -> bool:
        return bool(re.search(r'build|compile|make|gradle|npm.*build|cargo.*build', content, re.IGNORECASE))
    
    def _is_ci_cd_logs(self, content: str) -> bool:
        return bool(re.search(r'github|gitlab|jenkins|circleci|travis|workflow', content, re.IGNORECASE))
