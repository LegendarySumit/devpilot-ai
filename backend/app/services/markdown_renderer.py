from typing import Any
from datetime import datetime
from app.models.documentation_content import DocumentationContent, Section
from app.models.theme import Theme, PREDEFINED_THEMES
from app.models.renderer_output import RendererOutput, RendererMetadata
from app.models.documentation_content import (
    HeaderContent,
    ProseContent,
    FeatureListContent,
    CodeExampleContent,
    InstallationContent,
    UsageExamplesContent,
    APIReferenceContent,
)


class MarkdownRenderer:
    """Renders DocumentationContent to Markdown"""
    
    def __init__(self, theme: Theme = None):
        self.theme = theme or PREDEFINED_THEMES["professional"]
    
    def render(self, content: DocumentationContent) -> RendererOutput:
        """Render documentation content to Markdown"""
        markdown_lines = []
        
        sorted_sections = sorted(content.structure, key=lambda s: s.order)
        
        for section in sorted_sections:
            markdown_lines.append(self._render_section(section))
            markdown_lines.append("")
        
        markdown_text = "\n".join(markdown_lines).strip()
        
        metadata = RendererMetadata(
            word_count=len(markdown_text.split()),
            section_count=len(content.structure),
            estimated_read_time=self._estimate_read_time(markdown_text),
            generated_at=datetime.utcnow().isoformat(),
        )
        
        return RendererOutput(
            format="markdown",
            content=markdown_text,
            metadata=metadata,
        )
    
    def _render_section(self, section: Section) -> str:
        """Render a single section based on its type"""
        section_type = section.section_type
        content = section.content
        
        if section_type == "header":
            return self._render_header(content)
        elif section_type == "prose":
            return self._render_prose(content)
        elif section_type == "feature_list":
            return self._render_feature_list(content)
        elif section_type == "code_example":
            return self._render_code_example(content)
        elif section_type == "installation":
            return self._render_installation(content)
        elif section_type == "usage_examples":
            return self._render_usage_examples(content)
        elif section_type == "api_reference":
            return self._render_api_reference(content)
        else:
            return str(content)
    
    def _render_header(self, content: HeaderContent) -> str:
        """Render header section"""
        lines = []
        
        if self.theme.rules.layout.logo_position != "hidden" and content.logo_url:
            lines.append(f"![{content.title}]({content.logo_url})")
            lines.append("")
        
        h1_rules = self.theme.rules.typography.headings.h1
        
        if h1_rules.style == "centered":
            lines.append(f"<div align=\"center\">")
            lines.append("")
        
        if h1_rules.emoji:
            title = f"✨ {content.title}"
        else:
            title = content.title
        
        lines.append(f"# {title}")
        lines.append("")
        
        if content.subtitle:
            lines.append(f"_{content.subtitle}_")
            lines.append("")
        
        if h1_rules.style == "centered":
            lines.append("</div>")
        
        return "\n".join(lines)
    
    def _render_prose(self, content: ProseContent) -> str:
        """Render prose/text content"""
        return content.text
    
    def _render_feature_list(self, content: FeatureListContent) -> str:
        """Render feature list"""
        lines = ["## Features"]
        
        if self.theme.rules.emoji.enabled and self.theme.rules.emoji.in_lists:
            lines.append("")
            for item in content.items:
                emoji = "✨" if self.theme.rules.emoji.enabled else ""
                if item.description:
                    lines.append(f"- **{emoji} {item.name}** — {item.description}")
                else:
                    lines.append(f"- **{emoji} {item.name}**")
        else:
            lines.append("")
            for item in content.items:
                if item.description:
                    lines.append(f"- **{item.name}** — {item.description}")
                else:
                    lines.append(f"- **{item.name}**")
        
        return "\n".join(lines)
    
    def _render_code_example(self, content: CodeExampleContent) -> str:
        """Render code example"""
        lines = []
        
        if content.title:
            lines.append(f"## {content.title}")
            lines.append("")
        
        if content.description:
            lines.append(content.description)
            lines.append("")
        
        language = content.language if content.language != "plaintext" else "bash"
        lines.append(f"```{language}")
        lines.append(content.code)
        lines.append("```")
        
        return "\n".join(lines)
    
    def _render_installation(self, content: InstallationContent) -> str:
        """Render installation section"""
        lines = ["## Installation"]
        lines.append("")
        
        for method in content.methods:
            lines.append(f"### {method.method.title()}")
            lines.append("")
            lines.append(f"```bash")
            lines.append(method.command)
            lines.append("```")
            lines.append("")
            
            if method.description:
                lines.append(method.description)
                lines.append("")
        
        return "\n".join(lines).rstrip()
    
    def _render_usage_examples(self, content: UsageExamplesContent) -> str:
        """Render usage examples"""
        lines = ["## Usage"]
        lines.append("")
        
        for example in content.examples:
            if example.title:
                lines.append(f"### {example.title}")
                lines.append("")
            
            if example.description:
                lines.append(example.description)
                lines.append("")
            
            language = example.language if example.language != "plaintext" else "javascript"
            lines.append(f"```{language}")
            lines.append(example.code)
            lines.append("```")
            lines.append("")
        
        return "\n".join(lines).rstrip()
    
    def _render_api_reference(self, content: APIReferenceContent) -> str:
        """Render API reference"""
        lines = ["## API Reference"]
        lines.append("")
        
        for endpoint in content.endpoints:
            lines.append(f"### {endpoint.method.upper()} {endpoint.path}")
            
            if endpoint.description:
                lines.append("")
                lines.append(endpoint.description)
            
            lines.append("")
        
        return "\n".join(lines).rstrip()
    
    def _estimate_read_time(self, text: str) -> int:
        """Estimate read time in minutes (average 200 words per minute)"""
        word_count = len(text.split())
        return max(1, word_count // 200)
