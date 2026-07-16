"""
Documentation Processor - Generates documentation content from project model
"""
from typing import Dict, Any, List
from app.models.canonical_project_model import CanonicalProjectModel
from app.services.processing_framework import Processor


class DocumentationProcessor(Processor):
    """Generates documentation content from canonical project model"""
    
    stage_name = "documentation_processor"
    
    def process(self, canonical_model: CanonicalProjectModel, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation content"""
        
        # Build content sections
        content = {
            "identity": self._generate_identity_section(canonical_model),
            "purpose": self._generate_purpose_section(canonical_model),
            "tech_stack": self._generate_tech_section(canonical_model),
            "features": self._generate_features_section(canonical_model),
            "installation": self._generate_installation_section(canonical_model),
            "usage": self._generate_usage_section(canonical_model),
            "contributing": self._generate_contributing_section(),
            "license": self._generate_license_section(canonical_model),
        }
        
        # Generate assets needed for documentation
        assets = {
            "badges": self._generate_badges(canonical_model),
            "icons": self._generate_tech_icons(canonical_model),
            "images": [],
        }
        
        return {
            "content": content,
            "assets": assets,
            "sections": list(content.keys()),
            "ready_for_theme": True,
        }
    
    def _generate_identity_section(self, model: CanonicalProjectModel) -> Dict[str, str]:
        """Generate identity/header section"""
        
        identity = model.identity or {}
        return {
            "title": identity.get("name", "Project"),
            "subtitle": identity.get("description", ""),
        }
    
    def _generate_purpose_section(self, model: CanonicalProjectModel) -> Dict[str, str]:
        """Generate purpose/about section"""
        
        purpose = model.purpose or {}
        return {
            "heading": "About",
            "content": purpose.get("business_value", "A software project"),
            "target_audience": purpose.get("target_users", "Developers"),
        }
    
    def _generate_tech_section(self, model: CanonicalProjectModel) -> Dict[str, Any]:
        """Generate technology stack section"""
        
        tech = model.technical_stack or {}
        return {
            "heading": "Technology Stack",
            "languages": tech.get("languages", []),
            "frameworks": tech.get("frameworks", []),
            "databases": tech.get("databases", []),
            "tools": tech.get("tools", []),
        }
    
    def _generate_features_section(self, model: CanonicalProjectModel) -> Dict[str, Any]:
        """Generate features section"""
        
        features = model.features or []
        return {
            "heading": "Features",
            "items": features or ["Core functionality"],
            "count": len(features),
        }
    
    def _generate_installation_section(self, model: CanonicalProjectModel) -> Dict[str, Any]:
        """Generate installation section"""
        
        installation = model.installation or {}
        return {
            "heading": "Installation",
            "prerequisites": installation.get("prerequisites", ["Git"]),
            "steps": installation.get("steps", ["Clone repository", "Install dependencies", "Run application"]),
        }
    
    def _generate_usage_section(self, model: CanonicalProjectModel) -> Dict[str, Any]:
        """Generate usage section"""
        
        usage = model.usage or {}
        return {
            "heading": "Usage",
            "quick_start": usage.get("quick_start", "See installation steps"),
            "examples": usage.get("examples", []),
        }
    
    def _generate_contributing_section(self) -> Dict[str, str]:
        """Generate contributing section"""
        
        return {
            "heading": "Contributing",
            "content": "Contributions are welcome! Please feel free to submit a Pull Request.",
        }
    
    def _generate_license_section(self, model: CanonicalProjectModel) -> Dict[str, str]:
        """Generate license section"""
        
        status = model.status or {}
        license_type = status.get("license", "MIT")
        
        return {
            "heading": "License",
            "license_type": license_type,
            "year": "2024",
        }
    
    def _generate_badges(self, model: CanonicalProjectModel) -> List[Dict[str, str]]:
        """Generate documentation badges"""
        
        badges = []
        
        # Tech stack badges
        tech = model.technical_stack or {}
        for lang in tech.get("languages", [])[:3]:
            badges.append({
                "type": "language",
                "name": lang,
                "style": "flat-square",
            })
        
        # Status badge
        status = model.status or {}
        stage = status.get("development_stage", "Active")
        badges.append({
            "type": "status",
            "name": stage,
            "style": "flat-square",
        })
        
        # License badge
        license_type = status.get("license", "MIT")
        badges.append({
            "type": "license",
            "name": license_type,
            "style": "flat-square",
        })
        
        return badges
    
    def _generate_tech_icons(self, model: CanonicalProjectModel) -> List[Dict[str, str]]:
        """Generate tech stack icons"""
        
        icons = []
        tech = model.technical_stack or {}
        
        icon_map = {
            "Python": "python",
            "JavaScript": "javascript",
            "TypeScript": "typescript",
            "Java": "java",
            "Go": "go",
            "Rust": "rust",
            "React": "react",
            "Vue": "vue",
            "FastAPI": "fastapi",
            "Django": "django",
            "PostgreSQL": "postgresql",
            "MongoDB": "mongodb",
            "Docker": "docker",
        }
        
        all_techs = (
            tech.get("languages", []) +
            tech.get("frameworks", []) +
            tech.get("databases", [])
        )
        
        for tech_name in all_techs:
            icon_key = icon_map.get(tech_name, tech_name.lower())
            icons.append({
                "name": tech_name,
                "icon": icon_key,
            })
        
        return icons[:10]  # Limit to 10 icons
