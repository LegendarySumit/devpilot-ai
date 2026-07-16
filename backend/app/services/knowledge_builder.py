from typing import Optional, List, Dict, Any
from app.models.canonical_project_model import CanonicalProjectModel
from app.models.documentation_content import (
    DocumentationContent,
    DocumentationContentMetadata,
    Section,
    HeaderContent,
    ProseContent,
    FeatureListContent,
    FeatureItem,
    CodeExampleContent,
    InstallationContent,
    InstallationMethod,
    UsageExamplesContent,
    UsageExample,
)
from app.models.profile import Profile, PREDEFINED_PROFILES
from app.models.theme import Theme


class KnowledgeBuilder:
    """Transforms CPM into structured documentation content"""
    
    def __init__(self, cpm: CanonicalProjectModel, profile: Optional[Profile] = None, document_type: str = "README"):
        self.cpm = cpm
        self.profile = profile or PREDEFINED_PROFILES["developer"]
        self.document_type = document_type
        self.sections: List[Section] = []
    
    def build(self) -> DocumentationContent:
        """Build documentation content from CPM"""
        self._select_and_organize_content()
        
        metadata = DocumentationContentMetadata(
            document_type=self.document_type,
            profile=self.profile.id,
            generated_at="",
            source=self.cpm.source,
        )
        
        return DocumentationContent(
            metadata=metadata,
            structure=self.sections,
        )
    
    def _select_and_organize_content(self) -> None:
        """Select relevant content based on profile and document type"""
        order = 1
        
        if self.document_type == "README":
            order = self._build_readme(order)
        elif self.document_type == "CONTRIBUTING":
            order = self._build_contributing(order)
        elif self.document_type == "API":
            order = self._build_api_docs(order)
    
    def _build_readme(self, start_order: int) -> int:
        """Build README sections"""
        order = start_order
        
        order = self._add_header(order)
        order = self._add_description(order)
        order = self._add_features(order)
        order = self._add_installation(order)
        order = self._add_usage(order)
        order = self._add_contributing(order)
        order = self._add_license(order)
        
        return order
    
    def _build_contributing(self, start_order: int) -> int:
        """Build CONTRIBUTING.md sections"""
        order = start_order
        
        order = self._add_section(
            "contributing_intro",
            "prose",
            ProseContent(text="Thank you for your interest in contributing!"),
            order,
        )
        
        if self.cpm.community and self.cpm.community.contribution_guidelines:
            guidelines = self.cpm.community.contribution_guidelines
            if guidelines.process:
                order = self._add_section(
                    "contribution_process",
                    "prose",
                    ProseContent(text=guidelines.process),
                    order,
                )
        
        return order
    
    def _build_api_docs(self, start_order: int) -> int:
        """Build API.md sections"""
        order = start_order
        
        if self.cpm.usage and self.cpm.usage.api:
            order = self._add_section(
                "api_reference",
                "api_reference",
                self._build_api_content(),
                order,
            )
        
        return order
    
    def _add_header(self, order: int) -> int:
        """Add header section"""
        return self._add_section(
            "header",
            "header",
            HeaderContent(
                title=self.cpm.identity.name,
                subtitle=self.cpm.identity.short_description,
            ),
            order,
        )
    
    def _add_description(self, order: int) -> int:
        """Add description section"""
        if self.cpm.identity.full_description:
            return self._add_section(
                "description",
                "prose",
                ProseContent(text=self.cpm.identity.full_description),
                order,
            )
        return order
    
    def _add_features(self, order: int) -> int:
        """Add features section"""
        if self.cpm.features:
            items = [FeatureItem(name=f.name, description=f.description) for f in self.cpm.features]
            return self._add_section(
                "features",
                "feature_list",
                FeatureListContent(items=items),
                order,
            )
        return order
    
    def _add_installation(self, order: int) -> int:
        """Add installation section"""
        if self.cpm.installation:
            methods = [
                InstallationMethod(
                    method=m.method,
                    command=m.command,
                    description=m.supported_platforms[0] if m.supported_platforms else None,
                )
                for m in self.cpm.installation.installation_methods
            ]
            return self._add_section(
                "installation",
                "installation",
                InstallationContent(methods=methods),
                order,
            )
        return order
    
    def _add_usage(self, order: int) -> int:
        """Add usage section"""
        if self.cpm.usage and self.cpm.usage.examples:
            examples = [
                UsageExample(
                    title=e.title,
                    code=e.code or "",
                    language="plaintext",
                    description=e.description,
                )
                for e in self.cpm.usage.examples
            ]
            return self._add_section(
                "usage",
                "usage_examples",
                UsageExamplesContent(examples=examples),
                order,
            )
        return order
    
    def _add_contributing(self, order: int) -> int:
        """Add contributing section"""
        if self.cpm.community and self.cpm.community.contribution_guidelines:
            return self._add_section(
                "contributing",
                "prose",
                ProseContent(text="Contributions are welcome!"),
                order,
            )
        return order
    
    def _add_license(self, order: int) -> int:
        """Add license section"""
        if self.cpm.community and self.cpm.community.license:
            license_text = f"Licensed under {self.cpm.community.license.type}"
            return self._add_section(
                "license",
                "prose",
                ProseContent(text=license_text),
                order,
            )
        return order
    
    def _add_section(self, section_id: str, section_type: str, content: Any, order: int) -> int:
        """Add a section to the documentation"""
        section = Section(
            section_id=section_id,
            section_type=section_type,
            order=order,
            content=content,
        )
        self.sections.append(section)
        return order + 1
    
    def _build_api_content(self) -> Any:
        """Build API reference content from CPM"""
        from app.models.documentation_content import APIReferenceContent, APIEndpointItem, APIParameter
        
        endpoints = []
        if self.cpm.usage and self.cpm.usage.api:
            for endpoint in self.cpm.usage.api.endpoints:
                item = APIEndpointItem(
                    path=endpoint.path,
                    method=endpoint.method,
                    description=endpoint.description,
                )
                endpoints.append(item)
        
        return APIReferenceContent(endpoints=endpoints)
