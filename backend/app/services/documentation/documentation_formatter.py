"""
Documentation Formatter - Formats documentation content using theme
"""
from typing import Dict, Any
from app.models.documentation_content import DocumentationContent
from app.services.processing_framework import Formatter, EngineResponse


class DocumentationFormatter(Formatter):
    """Renders documentation content with theme"""
    
    stage_name = "documentation_formatter"
    
    def format(self, data: Dict[str, Any]) -> EngineResponse:
        """Format documentation content into markdown"""
        
        content = data.get("content", {})
        assets = data.get("assets", {})
        theme = data.get("theme", {})
        
        # Generate markdown from content and theme
        markdown = self._render_markdown(content, assets, theme)
        
        # Create documentation response
        doc_content = DocumentationContent(
            title=content.get("identity", {}).get("title", "Project"),
            markdown=markdown,
            sections=data.get("sections", []),
            quality_score=data.get("quality_score", 70),
        )
        
        return doc_content
    
    def _render_markdown(self, content: Dict, assets: Dict, theme: Dict) -> str:
        """Render markdown from content and theme"""
        
        parts = []
        
        # Render header
        identity = content.get("identity", {})
        parts.append(f"# {identity.get('title', 'Project')}")
        if identity.get("subtitle"):
            parts.append(f"\n{identity.get('subtitle')}\n")
        
        # Render badges if theme allows
        if theme.get("show_badges", True):
            badges = assets.get("badges", [])
            if badges:
                badge_line = ""
                for badge in badges:
                    badge_line += f"![{badge.get('name')}](https://img.shields.io/badge/{badge.get('name')}-{badge.get('style')})"
                if badge_line:
                    parts.append(f"\n{badge_line}\n")
        
        # Render purpose/about
        purpose = content.get("purpose", {})
        if purpose:
            parts.append(f"\n## {purpose.get('heading', 'About')}\n")
            parts.append(purpose.get("content", ""))
        
        # Render tech stack
        tech = content.get("tech_stack", {})
        if tech and (tech.get("languages") or tech.get("frameworks")):
            parts.append(f"\n## {tech.get('heading', 'Technology Stack')}\n")
            
            if tech.get("languages"):
                parts.append(f"**Languages:** {', '.join(tech.get('languages', []))}\n")
            if tech.get("frameworks"):
                parts.append(f"**Frameworks:** {', '.join(tech.get('frameworks', []))}\n")
            if tech.get("databases"):
                parts.append(f"**Databases:** {', '.join(tech.get('databases', []))}\n")
        
        # Render features
        features = content.get("features", {})
        if features and features.get("items"):
            parts.append(f"\n## {features.get('heading', 'Features')}\n")
            for item in features.get("items", []):
                parts.append(f"- {item}")
        
        # Render installation
        installation = content.get("installation", {})
        if installation:
            parts.append(f"\n## {installation.get('heading', 'Installation')}\n")
            
            if installation.get("prerequisites"):
                parts.append("### Prerequisites\n")
                for req in installation.get("prerequisites", []):
                    parts.append(f"- {req}")
            
            if installation.get("steps"):
                parts.append("\n### Steps\n")
                for i, step in enumerate(installation.get("steps", []), 1):
                    parts.append(f"{i}. {step}")
        
        # Render usage
        usage = content.get("usage", {})
        if usage:
            parts.append(f"\n## {usage.get('heading', 'Usage')}\n")
            if usage.get("quick_start"):
                parts.append(f"{usage.get('quick_start')}\n")
        
        # Render contributing
        contributing = content.get("contributing", {})
        if contributing:
            parts.append(f"\n## {contributing.get('heading', 'Contributing')}\n")
            parts.append(contributing.get("content", ""))
        
        # Render license
        license_section = content.get("license", {})
        if license_section:
            parts.append(f"\n## {license_section.get('heading', 'License')}\n")
            parts.append(f"This project is licensed under the {license_section.get('license_type', 'MIT')} License - see LICENSE file for details.\n")
        
        return "\n".join(parts)
