from app.services.llm_service import LLMService


class DocumentationContentEngine:
    def __init__(self) -> None:
        self.llm_service = LLMService()

    def generate_from_context(self, project_context: str, mode: str = "ai") -> dict[str, object]:
        if mode == "rule":
            return self._rule_based_content(project_context)

        prompt = (
            "Create structured README content data from project context. "
            "Return concise sections for title, description, features, tech_stack, installation, usage, license, author.\n\n"
            f"Project Context:\n{project_context}"
        )
        provider_output = self.llm_service.generate(prompt)

        return {
            "title": "Generated Project",
            "description": str(provider_output.get("result", "No description generated.")),
            "features": ["Core feature 1", "Core feature 2"],
            "tech_stack": ["Unknown"],
            "installation": ["Add installation steps"],
            "usage": ["Add usage examples"],
            "license": "MIT",
            "author": "Unknown",
            "metadata": {"mode": "ai"},
        }

    def _rule_based_content(self, project_context: str) -> dict[str, object]:
        return {
            "title": "Project",
            "description": project_context.strip() or "Project documentation.",
            "features": ["Add your features"],
            "tech_stack": ["Specify stack"],
            "installation": ["Provide installation commands"],
            "usage": ["Provide usage instructions"],
            "license": "MIT",
            "author": "Unknown",
            "metadata": {"mode": "rule"},
        }
