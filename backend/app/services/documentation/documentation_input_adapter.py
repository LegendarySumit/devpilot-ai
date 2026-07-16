"""
Documentation Input Adapter - Normalizes multiple input sources to CanonicalProjectModel
"""
from typing import Dict, Any, Optional
from app.models.canonical_project_model import CanonicalProjectModel
from app.services.processing_framework import InputAdapter


class DocumentationInputAdapter(InputAdapter):
    """Converts multiple input types to canonical project model"""
    
    stage_name = "documentation_input_adapter"
    
    def adapt(self, raw_input: Dict[str, Any] | str) -> CanonicalProjectModel:
        """Parse raw input to canonical project model"""
        
        if isinstance(raw_input, str):
            return self._parse_project_idea(raw_input)
        
        if isinstance(raw_input, dict):
            input_type = raw_input.get("input_type", "idea")
            
            if input_type == "idea":
                return self._parse_project_idea(raw_input.get("content", raw_input.get("description", "")))
            elif input_type == "github":
                return self._parse_github_repository(raw_input)
            elif input_type == "readme":
                return self._parse_existing_readme(raw_input)
            elif input_type == "local_project":
                return self._parse_local_project(raw_input)
        
        # Fallback: treat as idea
        return self._parse_project_idea(str(raw_input))
    
    def _parse_project_idea(self, text: str) -> CanonicalProjectModel:
        """Parse project idea from free-form text"""
        
        return CanonicalProjectModel(
            identity=self._extract_identity(text),
            purpose=self._extract_purpose(text),
            technical_stack=self._extract_tech_stack(text),
            features=self._extract_features(text),
            installation=self._extract_installation(text),
            usage=self._extract_usage(text),
            status=self._extract_status(text),
        )
    
    def _parse_github_repository(self, data: Dict[str, Any]) -> CanonicalProjectModel:
        """Parse GitHub repository data"""
        
        return CanonicalProjectModel(
            identity=self._extract_github_identity(data),
            purpose=self._extract_github_purpose(data),
            technical_stack=self._extract_github_tech(data),
            features=self._extract_github_features(data),
            status=self._extract_github_status(data),
        )
    
    def _parse_existing_readme(self, data: Dict[str, Any]) -> CanonicalProjectModel:
        """Parse existing README markdown"""
        
        content = data.get("content", data.get("markdown", ""))
        
        return CanonicalProjectModel(
            identity=self._extract_identity_from_readme(content),
            purpose=self._extract_purpose_from_readme(content),
            technical_stack=self._extract_tech_from_readme(content),
            features=self._extract_features_from_readme(content),
        )
    
    def _parse_local_project(self, data: Dict[str, Any]) -> CanonicalProjectModel:
        """Parse local project structure and files"""
        
        return CanonicalProjectModel(
            identity=self._extract_local_identity(data),
            purpose=self._extract_local_purpose(data),
            technical_stack=self._extract_local_tech(data),
            features=self._extract_local_features(data),
        )
    
    def _extract_identity(self, text: str) -> Dict[str, Any]:
        """Extract project name and basic identity"""
        lines = text.strip().split("\n")
        
        # First line is often the project name
        name = lines[0].strip() if lines else "Project"
        
        # Look for description in following lines
        description = ""
        for line in lines[1:5]:
            if line.strip() and not any(c in line for c in ["#", "*", "-"]):
                description = line.strip()
                break
        
        return {
            "name": name,
            "description": description or name,
        }
    
    def _extract_purpose(self, text: str) -> Dict[str, Any]:
        """Extract project purpose"""
        
        return {
            "business_value": text[:500] if text else "A software project",
            "target_users": "Developers",
        }
    
    def _extract_tech_stack(self, text: str) -> Dict[str, Any]:
        """Extract technology stack"""
        
        text_lower = text.lower()
        
        languages = []
        if any(w in text_lower for w in ["python", "fastapi", "django", "flask"]):
            languages.append("Python")
        if any(w in text_lower for w in ["javascript", "typescript", "node", "react", "vue", "nextjs"]):
            languages.append("JavaScript/TypeScript")
        if any(w in text_lower for w in ["java", "spring"]):
            languages.append("Java")
        
        frameworks = []
        if "fastapi" in text_lower:
            frameworks.append("FastAPI")
        if "react" in text_lower:
            frameworks.append("React")
        if "django" in text_lower:
            frameworks.append("Django")
        
        databases = []
        if any(w in text_lower for w in ["postgres", "postgresql"]):
            databases.append("PostgreSQL")
        if "mongodb" in text_lower:
            databases.append("MongoDB")
        if "mysql" in text_lower:
            databases.append("MySQL")
        
        return {
            "languages": languages or ["Unknown"],
            "frameworks": frameworks or [],
            "databases": databases or [],
            "tools": [],
        }
    
    def _extract_features(self, text: str) -> list:
        """Extract features from text"""
        
        # Look for feature lists marked with -, *, or numbers
        features = []
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if line and any(line.startswith(m) for m in ["- ", "* ", "• "]):
                features.append(line[2:].strip())
            elif line and line[0].isdigit() and ". " in line:
                features.append(line.split(". ", 1)[1].strip())
        
        return features or ["Core functionality"]
    
    def _extract_installation(self, text: str) -> Dict[str, Any]:
        """Extract installation instructions"""
        
        return {
            "prerequisites": ["Git", "Python 3.8+"],
            "steps": [
                "Clone the repository",
                "Install dependencies",
                "Configure environment",
                "Run the application",
            ],
        }
    
    def _extract_usage(self, text: str) -> Dict[str, Any]:
        """Extract usage information"""
        
        return {
            "quick_start": "See installation steps",
            "examples": [],
        }
    
    def _extract_status(self, text: str) -> Dict[str, Any]:
        """Extract project status"""
        
        return {
            "development_stage": "Active",
            "license": "MIT",
        }
    
    # GitHub parsing methods
    def _extract_github_identity(self, data: Dict) -> Dict[str, Any]:
        return {
            "name": data.get("name", data.get("full_name", "Project")),
            "description": data.get("description", ""),
        }
    
    def _extract_github_purpose(self, data: Dict) -> Dict[str, Any]:
        return {"business_value": data.get("description", ""), "target_users": "Developers"}
    
    def _extract_github_tech(self, data: Dict) -> Dict[str, Any]:
        return {
            "languages": data.get("languages", []),
            "frameworks": [],
            "databases": [],
            "tools": [],
        }
    
    def _extract_github_features(self, data: Dict) -> list:
        return data.get("features", [])
    
    def _extract_github_status(self, data: Dict) -> Dict[str, Any]:
        return {
            "development_stage": "Active" if not data.get("archived") else "Archived",
            "license": data.get("license", ""),
        }
    
    # README parsing methods
    def _extract_identity_from_readme(self, content: str) -> Dict[str, Any]:
        lines = content.split("\n")
        name = ""
        description = ""
        
        for i, line in enumerate(lines[:10]):
            if line.startswith("#"):
                name = line.replace("#", "").strip()
                if i + 1 < len(lines):
                    description = lines[i + 1].strip()
                break
        
        return {"name": name or "Project", "description": description}
    
    def _extract_purpose_from_readme(self, content: str) -> Dict[str, Any]:
        return {"business_value": content[:300], "target_users": "Developers"}
    
    def _extract_tech_from_readme(self, content: str) -> Dict[str, Any]:
        return {"languages": [], "frameworks": [], "databases": [], "tools": []}
    
    def _extract_features_from_readme(self, content: str) -> list:
        return []
    
    # Local project parsing methods
    def _extract_local_identity(self, data: Dict) -> Dict[str, Any]:
        return {"name": data.get("project_name", "Project"), "description": data.get("description", "")}
    
    def _extract_local_purpose(self, data: Dict) -> Dict[str, Any]:
        return {"business_value": data.get("description", ""), "target_users": "Developers"}
    
    def _extract_local_tech(self, data: Dict) -> Dict[str, Any]:
        return data.get("tech_stack", {"languages": [], "frameworks": [], "databases": [], "tools": []})
    
    def _extract_local_features(self, data: Dict) -> list:
        return data.get("features", [])
