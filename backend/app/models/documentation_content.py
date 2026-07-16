from typing import Optional, List, Any, Literal
from pydantic import BaseModel


SectionType = Literal[
    "header",
    "prose",
    "feature_list",
    "code_example",
    "installation",
    "usage_examples",
    "api_reference",
    "table",
    "badges",
    "toc",
    "media",
]


class HeaderContent(BaseModel):
    logo_url: Optional[str] = None
    title: str
    subtitle: Optional[str] = None


class ProseContent(BaseModel):
    text: str


class FeatureItem(BaseModel):
    name: str
    description: Optional[str] = None


class FeatureListContent(BaseModel):
    items: List[FeatureItem] = []


class CodeExampleContent(BaseModel):
    title: str
    description: Optional[str] = None
    code: str
    language: str = "plaintext"


class InstallationMethod(BaseModel):
    method: str
    command: str
    description: Optional[str] = None


class InstallationContent(BaseModel):
    methods: List[InstallationMethod] = []


class UsageExample(BaseModel):
    title: str
    code: str
    language: str = "plaintext"
    description: Optional[str] = None


class UsageExamplesContent(BaseModel):
    examples: List[UsageExample] = []


class APIParameter(BaseModel):
    name: str
    type: str
    required: bool = False
    description: Optional[str] = None


class APIEndpointItem(BaseModel):
    path: str
    method: str
    description: Optional[str] = None
    parameters: List[APIParameter] = []
    response: Optional[str] = None


class APIReferenceContent(BaseModel):
    endpoints: List[APIEndpointItem] = []


class TableRow(BaseModel):
    cells: List[str]


class TableContent(BaseModel):
    headers: List[str]
    rows: List[TableRow]


class BadgeItem(BaseModel):
    type: str
    value: str
    url: Optional[str] = None


class BadgesContent(BaseModel):
    badges: List[BadgeItem] = []


class TOCItem(BaseModel):
    text: str
    level: int
    anchor: str


class TOCContent(BaseModel):
    items: List[TOCItem] = []


class MediaItem(BaseModel):
    type: Literal["image", "video", "embed"]
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None


class MediaContent(BaseModel):
    items: List[MediaItem] = []


class Section(BaseModel):
    section_id: str
    section_type: SectionType
    order: int
    content: Any
    metadata: Optional[dict] = None


class DocumentationContentMetadata(BaseModel):
    document_type: str
    profile: Optional[str] = None
    generated_at: str
    source: Optional[str] = None


class DocumentationContent(BaseModel):
    metadata: DocumentationContentMetadata
    structure: List[Section] = []
    
    def get_section(self, section_id: str) -> Optional[Section]:
        for section in self.structure:
            if section.section_id == section_id:
                return section
        return None
    
    def add_section(self, section: Section) -> None:
        self.structure.append(section)
    
    def remove_section(self, section_id: str) -> None:
        self.structure = [s for s in self.structure if s.section_id != section_id]
