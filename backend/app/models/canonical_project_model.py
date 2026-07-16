from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class Identity(BaseModel):
    name: str
    slug: Optional[str] = None
    short_description: str
    full_description: Optional[str] = None
    tagline: Optional[str] = None
    homepage: Optional[HttpUrl] = None


class Purpose(BaseModel):
    problem_solved: Optional[str] = None
    target_audience: List[str] = []
    use_cases: List[str] = []
    differentiators: List[str] = []
    similar_projects: List[str] = []


class Dependency(BaseModel):
    name: str
    version: Optional[str] = None
    category: Optional[str] = None


class TechnicalStack(BaseModel):
    primary_language: Optional[str] = None
    framework: Optional[str] = None
    runtime: Optional[str] = None
    database: Optional[str] = None
    dependencies: List[Dependency] = []
    architecture_pattern: Optional[str] = None


class Feature(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class Requirement(BaseModel):
    name: str
    version: Optional[str] = None
    note: Optional[str] = None


class InstallationMethod(BaseModel):
    method: str
    command: str
    supported_platforms: List[str] = []


class Installation(BaseModel):
    requirements: List[Requirement] = []
    steps: List[str] = []
    installation_methods: List[InstallationMethod] = []


class Example(BaseModel):
    title: str
    description: Optional[str] = None
    code: Optional[str] = None


class EnvironmentVariable(BaseModel):
    name: str
    description: Optional[str] = None
    required: bool = False
    example: Optional[str] = None


class Configuration(BaseModel):
    config_file: Optional[str] = None
    environment_variables: List[EnvironmentVariable] = []
    common_settings: List[str] = []


class Command(BaseModel):
    name: str
    description: Optional[str] = None
    usage: Optional[str] = None


class APIEndpoint(BaseModel):
    path: str
    method: str
    description: Optional[str] = None
    parameters: List[str] = []
    response: Optional[str] = None


class API(BaseModel):
    available: bool = False
    base_url: Optional[HttpUrl] = None
    authentication: Optional[str] = None
    endpoints: List[APIEndpoint] = []


class Usage(BaseModel):
    quick_start: Optional[str] = None
    examples: List[Example] = []
    configuration: Optional[Configuration] = None
    commands: List[Command] = []
    api: Optional[API] = None


class Maintainer(BaseModel):
    name: str
    email: Optional[str] = None
    github: Optional[str] = None
    role: Optional[str] = None


class Contributor(BaseModel):
    name: str
    contributions: Optional[int] = None


class License(BaseModel):
    type: str
    url: Optional[HttpUrl] = None


class ContributionGuidelines(BaseModel):
    accepting_contributions: bool = False
    process: Optional[str] = None
    development_setup: Optional[str] = None
    testing: Optional[str] = None


class SupportChannel(BaseModel):
    type: str
    url: Optional[HttpUrl] = None


class Community(BaseModel):
    maintainers: List[Maintainer] = []
    contributors: List[Contributor] = []
    license: Optional[License] = None
    contribution_guidelines: Optional[ContributionGuidelines] = None
    code_of_conduct: Optional[str] = None
    support_channels: List[SupportChannel] = []


class Logo(BaseModel):
    url: Optional[HttpUrl] = None
    description: Optional[str] = None


class Screenshot(BaseModel):
    title: str
    url: HttpUrl
    description: Optional[str] = None


class Demo(BaseModel):
    available: bool = False
    url: Optional[HttpUrl] = None
    video: Optional[HttpUrl] = None


class Badge(BaseModel):
    type: str
    value: str
    url: Optional[HttpUrl] = None


class Social(BaseModel):
    repository: Optional[HttpUrl] = None
    npm: Optional[HttpUrl] = None
    pypi: Optional[HttpUrl] = None
    docker: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    discord: Optional[HttpUrl] = None


class Assets(BaseModel):
    logo: Optional[Logo] = None
    screenshots: List[Screenshot] = []
    demo: Optional[Demo] = None
    badges: List[Badge] = []
    social: Optional[Social] = None


class Status(BaseModel):
    version: Optional[str] = None
    release_date: Optional[str] = None
    maturity: str = "alpha"
    active_development: bool = True
    last_update: Optional[str] = None
    roadmap: Optional[str] = None
    known_issues: List[str] = []


class Metadata(BaseModel):
    keywords: List[str] = []
    categories: List[str] = []
    deployment_targets: List[str] = []
    performance_characteristics: Optional[str] = None
    scalability_notes: Optional[str] = None


class CanonicalProjectModel(BaseModel):
    version: str = "1.0"
    last_updated: datetime = None
    source: str
    
    identity: Identity
    purpose: Optional[Purpose] = None
    technical_stack: Optional[TechnicalStack] = None
    features: List[Feature] = []
    installation: Optional[Installation] = None
    usage: Optional[Usage] = None
    community: Optional[Community] = None
    assets: Optional[Assets] = None
    status: Optional[Status] = None
    metadata: Optional[Metadata] = None
    
    def __init__(self, **data):
        if data.get('last_updated') is None:
            data['last_updated'] = datetime.utcnow()
        super().__init__(**data)
