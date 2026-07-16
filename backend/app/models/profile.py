from typing import List, Literal
from pydantic import BaseModel


class ProfileEmphasis(BaseModel):
    technical_depth: Literal["low", "medium", "high"] = "medium"
    visual_appeal: Literal["low", "medium", "high"] = "medium"
    community: Literal["low", "medium", "high"] = "medium"
    usage_simplicity: Literal["low", "medium", "high"] = "high"


class Profile(BaseModel):
    id: str
    label: str
    description: str
    priorities: List[str] = []
    emphasis: ProfileEmphasis = ProfileEmphasis()
    tone: Literal["professional", "welcoming", "technical", "personal", "professional_friendly", "collaborative"] = "professional"
    sections_to_highlight: List[str] = []
    sections_to_minimize: List[str] = []


# Predefined profiles
RECRUITER_PROFILE = Profile(
    id="recruiter",
    label="Recruiter",
    description="Evaluating technical skills and project maturity",
    priorities=[
        "technologies",
        "architecture",
        "achievements",
        "team_quality",
        "project_maturity",
    ],
    emphasis=ProfileEmphasis(
        technical_depth="high",
        visual_appeal="medium",
        community="low",
        usage_simplicity="low",
    ),
    tone="professional",
    sections_to_highlight=[
        "Tech Stack",
        "Architecture",
        "Key Achievements",
        "Contributors",
    ],
    sections_to_minimize=[
        "Contributing Guidelines",
        "Community",
        "Troubleshooting",
    ],
)

OPEN_SOURCE_CONTRIBUTOR_PROFILE = Profile(
    id="open_source_contributor",
    label="Open Source Contributor",
    description="Wants to contribute and understand the project",
    priorities=[
        "contribution_guidelines",
        "development_setup",
        "roadmap",
        "community",
        "code_organization",
    ],
    emphasis=ProfileEmphasis(
        technical_depth="high",
        visual_appeal="low",
        community="high",
        usage_simplicity="high",
    ),
    tone="welcoming",
    sections_to_highlight=[
        "Contributing",
        "Development Setup",
        "Roadmap",
        "Community",
        "Support Channels",
    ],
    sections_to_minimize=[
        "Business Value",
        "Marketing",
    ],
)

CLIENT_PROFILE = Profile(
    id="client",
    label="Client/Business User",
    description="Evaluating business value and implementation",
    priorities=[
        "business_value",
        "features",
        "demo",
        "deployment",
        "support",
    ],
    emphasis=ProfileEmphasis(
        technical_depth="low",
        visual_appeal="high",
        community="low",
        usage_simplicity="high",
    ),
    tone="professional_friendly",
    sections_to_highlight=[
        "Features",
        "Demo",
        "Use Cases",
        "Deployment Options",
        "Support",
    ],
    sections_to_minimize=[
        "Architecture",
        "Dependencies",
        "Contributing Guidelines",
    ],
)

DEVELOPER_PROFILE = Profile(
    id="developer",
    label="Developer/Engineer",
    description="Using the project in their own work",
    priorities=[
        "quick_start",
        "examples",
        "api",
        "configuration",
        "troubleshooting",
    ],
    emphasis=ProfileEmphasis(
        technical_depth="high",
        visual_appeal="low",
        community="medium",
        usage_simplicity="high",
    ),
    tone="technical",
    sections_to_highlight=[
        "Installation",
        "Quick Start",
        "Examples",
        "API Reference",
        "Configuration",
    ],
    sections_to_minimize=[
        "Contributing Guidelines",
        "Roadmap",
    ],
)

PORTFOLIO_PROFILE = Profile(
    id="portfolio",
    label="Portfolio/Personal Brand",
    description="Showcasing the creator's work and skills",
    priorities=[
        "impact",
        "visual_presentation",
        "achievements",
        "creator_story",
        "live_demo",
    ],
    emphasis=ProfileEmphasis(
        technical_depth="medium",
        visual_appeal="high",
        community="low",
        usage_simplicity="high",
    ),
    tone="personal",
    sections_to_highlight=[
        "About the Creator",
        "Demo/Screenshots",
        "Key Features",
        "Impact/Metrics",
        "Contact/Social",
    ],
    sections_to_minimize=[
        "Contributing Guidelines",
        "Troubleshooting",
    ],
)

TEAM_PROFILE = Profile(
    id="team",
    label="Internal Team",
    description="Team members collaborating on a project",
    priorities=[
        "development_setup",
        "project_status",
        "deployment",
        "team_members",
        "roadmap",
    ],
    emphasis=ProfileEmphasis(
        technical_depth="high",
        visual_appeal="low",
        community="high",
        usage_simplicity="medium",
    ),
    tone="collaborative",
    sections_to_highlight=[
        "Setup",
        "Status",
        "Team",
        "Roadmap",
        "Support Channels",
    ],
    sections_to_minimize=[
        "Marketing",
        "Public Community",
    ],
)

PREDEFINED_PROFILES = {
    "recruiter": RECRUITER_PROFILE,
    "open_source_contributor": OPEN_SOURCE_CONTRIBUTOR_PROFILE,
    "client": CLIENT_PROFILE,
    "developer": DEVELOPER_PROFILE,
    "portfolio": PORTFOLIO_PROFILE,
    "team": TEAM_PROFILE,
}
