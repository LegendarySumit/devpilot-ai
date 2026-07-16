from typing import Dict, Any, Optional, Tuple
from app.services.context_extractor_base import ContextExtractor, ExtractionMetadata
from app.services.idea_context_extractor import IdeaContextExtractor
from app.services.github_context_extractor import GitHubContextExtractor
from app.services.readme_context_extractor import ReadmeContextExtractor
from app.services.local_project_context_extractor import LocalProjectContextExtractor
from app.services.knowledge_builder import KnowledgeBuilder
from app.services.markdown_renderer import MarkdownRenderer
from app.models.canonical_project_model import CanonicalProjectModel
from app.models.documentation_content import DocumentationContent
from app.models.renderer_output import RendererOutput
from app.models.profile import Profile, PREDEFINED_PROFILES
from app.models.theme import Theme, PREDEFINED_THEMES


class DocumentationStudioOrchestrator:
    """Orchestrates the entire Documentation Studio pipeline"""
    
    def __init__(self):
        self.extractors = {
            "project_idea": IdeaContextExtractor(),
            "github_repository": GitHubContextExtractor(),
            "existing_readme": ReadmeContextExtractor(),
            "local_project": LocalProjectContextExtractor(),
        }
    
    def generate_documentation(
        self,
        input_data: Any,
        input_type: str,
        profile_id: Optional[str] = None,
        theme_id: Optional[str] = None,
        document_type: str = "README",
    ) -> Dict[str, Any]:
        """
        End-to-end pipeline: Input → CPM → Content → Markdown
        
        Args:
            input_data: Raw input (string, dict, etc.)
            input_type: Type of input ("project_idea", "github_repository", etc.)
            profile_id: Profile ID (e.g., "developer", "recruiter")
            theme_id: Theme ID (e.g., "professional", "open_source")
            document_type: Type of document to generate ("README", "CONTRIBUTING", etc.)
        
        Returns:
            Dictionary with:
            - cpm: CanonicalProjectModel
            - content: DocumentationContent
            - markdown: Final rendered Markdown
            - metadata: Extraction and rendering metadata
        """
        
        profile = PREDEFINED_PROFILES.get(profile_id or "developer")
        theme = PREDEFINED_THEMES.get(theme_id or "professional")
        
        cpm, extraction_metadata = self.extract_context(input_data, input_type)
        
        content = self.build_content(cpm, profile, document_type)
        
        output = self.render_output(content, theme)
        
        return {
            "cpm": cpm,
            "content": content,
            "markdown": output.content,
            "metadata": {
                "extraction": extraction_metadata,
                "rendering": output.metadata.model_dump(),
            },
        }
    
    def extract_context(self, input_data: Any, input_type: str) -> Tuple[CanonicalProjectModel, ExtractionMetadata]:
        """Extract context based on input type"""
        extractor = self.extractors.get(input_type)
        
        if not extractor:
            raise ValueError(f"Unknown input type: {input_type}")
        
        if not extractor.validate_input(input_data):
            raise ValueError(f"Invalid input for {input_type}")
        
        return extractor.extract(input_data)
    
    def build_content(
        self,
        cpm: CanonicalProjectModel,
        profile: Optional[Profile] = None,
        document_type: str = "README",
    ) -> DocumentationContent:
        """Build structured documentation content"""
        profile = profile or PREDEFINED_PROFILES["developer"]
        builder = KnowledgeBuilder(cpm, profile, document_type)
        return builder.build()
    
    def render_output(self, content: DocumentationContent, theme: Optional[Theme] = None) -> RendererOutput:
        """Render documentation content to output format"""
        theme = theme or PREDEFINED_THEMES["professional"]
        renderer = MarkdownRenderer(theme)
        return renderer.render(content)
    
    def batch_generate(self, input_data: Any, input_type: str) -> Dict[str, str]:
        """
        Generate documentation for all profiles and themes
        
        Returns:
            Dictionary with keys like "developer_professional", "recruiter_open_source", etc.
        """
        cpm, _ = self.extract_context(input_data, input_type)
        
        results = {}
        
        for profile_id, profile in PREDEFINED_PROFILES.items():
            for theme_id, theme in PREDEFINED_THEMES.items():
                key = f"{profile_id}_{theme_id}"
                
                content = self.build_content(cpm, profile)
                output = self.render_output(content, theme)
                results[key] = output.content
        
        return results
