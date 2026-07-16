from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel


class HeadingStyle(BaseModel):
    case: Literal["title_case", "UPPERCASE", "lowercase"] = "title_case"
    emoji: bool = False
    style: Literal["centered", "left", "right"] = "left"
    underline: Literal["single_line", "double_line", "equals", "dashes", "none"] = "none"
    spacing_above: Literal["single", "double", "triple"] = "single"
    spacing_below: Literal["single", "double"] = "single"


class TypographyHeadings(BaseModel):
    h1: HeadingStyle = HeadingStyle(style="centered")
    h2: HeadingStyle = HeadingStyle()
    h3: HeadingStyle = HeadingStyle()


class BodyTextStyle(BaseModel):
    alignment: Literal["left", "justified"] = "left"
    emphasis_style: Literal["bold", "italic", "both", "none"] = "bold"
    maximum_line_length: int = 100
    paragraph_spacing: Literal["single", "double"] = "single"


class Typography(BaseModel):
    headings: TypographyHeadings = TypographyHeadings()
    body_text: BodyTextStyle = BodyTextStyle()


class BadgeRules(BaseModel):
    enabled: bool = True
    style: Literal["shields", "flat", "plastic", "custom"] = "shields"
    placement: Literal["below_title", "end_of_description", "separate_line"] = "below_title"
    density: Literal["sparse", "moderate", "dense"] = "sparse"
    organization: Literal["by_category", "all_together"] = "by_category"
    show_categories: List[str] = ["version", "license", "build"]


class EmojiRules(BaseModel):
    enabled: bool = False
    usage: Literal["none", "light", "moderate", "heavy"] = "none"
    in_headings: bool = False
    in_lists: bool = False
    in_tables: bool = False
    style: Literal["unicode", "emoji", "text_alternatives"] = "unicode"


class ColorRules(BaseModel):
    primary: Optional[str] = None
    accent: Optional[str] = None
    scheme: Literal["monochrome", "grayscale", "colorful", "custom"] = "monochrome"
    highlight_code: bool = True
    link_color: str = "standard"


class LayoutRules(BaseModel):
    logo_position: Literal["above_title", "beside_title", "hidden"] = "above_title"
    logo_size: Literal["small", "medium", "large"] = "medium"
    feature_display: Literal["bulleted_list", "numbered_list", "card_grid", "description_list"] = "bulleted_list"
    code_block_style: Literal["fenced", "indented", "highlighted"] = "fenced"
    code_highlight: bool = True
    table_style: Literal["markdown", "grid", "fancy_grid"] = "markdown"
    horizontal_rules: Literal["none", "dashes", "equals", "stars", "subtle"] = "dashes"
    feature_images: Literal["hidden", "thumbnail", "full_width"] = "thumbnail"


class TableOfContentsRules(BaseModel):
    enabled: bool = True
    position: Literal["after_description", "after_badges", "at_end"] = "after_description"
    depth: int = 2
    style: Literal["bulleted", "numbered", "markdown_style"] = "markdown_style"


class BadgesSection(BaseModel):
    enabled: bool = True
    show: List[str] = ["version", "license", "build"]


class BadgesDivider(BaseModel):
    enabled: bool = True
    style: Literal["line", "blank"] = "line"


class FooterRules(BaseModel):
    enabled: bool = True
    style: Literal["minimal", "standard", "detailed"] = "standard"
    includes: List[str] = ["license", "credits"]


class SectionRules(BaseModel):
    table_of_contents: TableOfContentsRules = TableOfContentsRules()
    badges: BadgesSection = BadgesSection()
    badges_divider: BadgesDivider = BadgesDivider()
    footer: FooterRules = FooterRules()


class SpacingRules(BaseModel):
    section_gap: Literal["compact", "single", "double", "triple"] = "double"
    item_gap: Literal["compact", "single", "double"] = "single"
    heading_above: Literal["none", "single", "double", "triple"] = "double"
    heading_below: Literal["none", "single", "double"] = "single"
    list_indentation: int = 2
    paragraph_spacing: Literal["single", "double"] = "single"


class ThemeRules(BaseModel):
    typography: Typography = Typography()
    badges: BadgeRules = BadgeRules()
    emoji: EmojiRules = EmojiRules()
    colors: ColorRules = ColorRules()
    layout: LayoutRules = LayoutRules()
    sections: SectionRules = SectionRules()
    spacing: SpacingRules = SpacingRules()


class Theme(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    rules: ThemeRules = ThemeRules()
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "professional",
                    "name": "Professional",
                    "description": "Clean, business-appropriate documentation",
                }
            ]
        }


# Predefined themes
PROFESSIONAL_THEME = Theme(
    id="professional",
    name="Professional",
    description="Clean, business-appropriate documentation",
    rules=ThemeRules(
        typography=Typography(
            headings=TypographyHeadings(
                h1=HeadingStyle(style="centered"),
                h2=HeadingStyle(style="left"),
            )
        ),
        badges=BadgeRules(enabled=True, density="sparse"),
        emoji=EmojiRules(enabled=False),
        layout=LayoutRules(feature_display="bulleted_list"),
        spacing=SpacingRules(section_gap="double"),
    ),
)

MINIMAL_THEME = Theme(
    id="minimal",
    name="Minimal",
    description="Lean, developer-focused documentation",
    rules=ThemeRules(
        typography=Typography(
            headings=TypographyHeadings(
                h1=HeadingStyle(style="left"),
            )
        ),
        badges=BadgeRules(enabled=False),
        emoji=EmojiRules(enabled=False),
        layout=LayoutRules(feature_display="bulleted_list"),
        spacing=SpacingRules(section_gap="single"),
    ),
)

OPEN_SOURCE_THEME = Theme(
    id="open_source",
    name="Open Source",
    description="Community-friendly documentation with personality",
    rules=ThemeRules(
        typography=Typography(
            headings=TypographyHeadings(
                h1=HeadingStyle(style="centered", emoji=True),
            )
        ),
        badges=BadgeRules(enabled=True, density="dense"),
        emoji=EmojiRules(enabled=True, usage="moderate"),
        layout=LayoutRules(feature_display="bulleted_list"),
        spacing=SpacingRules(section_gap="double"),
    ),
)

PORTFOLIO_THEME = Theme(
    id="portfolio",
    name="Portfolio",
    description="Visually appealing portfolio documentation",
    rules=ThemeRules(
        typography=Typography(
            headings=TypographyHeadings(
                h1=HeadingStyle(style="centered", emoji=True),
            )
        ),
        badges=BadgeRules(enabled=True, density="moderate"),
        emoji=EmojiRules(enabled=True, usage="heavy"),
        layout=LayoutRules(feature_display="card_grid", feature_images="full_width"),
        spacing=SpacingRules(section_gap="double"),
    ),
)

PREDEFINED_THEMES = {
    "professional": PROFESSIONAL_THEME,
    "minimal": MINIMAL_THEME,
    "open_source": OPEN_SOURCE_THEME,
    "portfolio": PORTFOLIO_THEME,
}
