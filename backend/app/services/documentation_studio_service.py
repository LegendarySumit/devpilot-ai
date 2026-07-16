from app.services.documentation_content_engine import DocumentationContentEngine
from app.services.documentation_theme_engine import DocumentationThemeEngine
from app.services.markdown_renderer import MarkdownRenderer


class DocumentationStudioService:
    def __init__(self) -> None:
        self.content_engine = DocumentationContentEngine()
        self.theme_engine = DocumentationThemeEngine()
        self.renderer = MarkdownRenderer()

    def generate_readme(
        self,
        project_context: str,
        theme_name: str = "professional",
        theme_variant: str = "light",
        mode: str = "ai",
    ) -> dict[str, object]:
        content = self.content_engine.generate_from_context(project_context=project_context, mode=mode)
        theme = self.theme_engine.resolve(theme=theme_name, variant=theme_variant)
        markdown = self.renderer.render_readme(content=content, theme=theme)

        return {
            "output_type": "README",
            "content": content,
            "theme": theme,
            "markdown": markdown,
        }
