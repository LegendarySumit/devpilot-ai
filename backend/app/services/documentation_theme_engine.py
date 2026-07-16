class DocumentationThemeEngine:
    THEMES: dict[str, dict[str, object]] = {
        "professional": {
            "variants": ["light", "minimal", "compact"],
            "capabilities": ["badges", "tables", "footer", "api", "project_tree", "images"],
            "layout": {
                "header": "centered",
                "badges": True,
                "horizontal_rules": True,
                "emoji": "minimal",
            },
        },
        "minimal": {
            "variants": ["light", "compact"],
            "capabilities": ["footer", "api"],
            "layout": {
                "header": "left",
                "badges": False,
                "horizontal_rules": False,
                "emoji": "none",
            },
        },
        "terminal": {
            "variants": ["ascii", "compact"],
            "capabilities": ["ascii", "cli", "tree", "commands", "monospace"],
            "layout": {
                "header": "ascii",
                "badges": False,
                "horizontal_rules": False,
                "emoji": "none",
            },
        },
    }

    def resolve(self, theme: str, variant: str) -> dict[str, object]:
        base = self.THEMES.get(theme, self.THEMES["professional"])
        selected_variant = variant if variant in base["variants"] else base["variants"][0]

        return {
            "name": theme if theme in self.THEMES else "professional",
            "variant": selected_variant,
            "capabilities": base["capabilities"],
            "layout": base["layout"],
        }
