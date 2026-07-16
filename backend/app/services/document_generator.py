class DocumentGenerator:
    def generate(
        self,
        provider_output: dict[str, object],
        analysis: dict[str, object],
        structure: dict[str, object],
        studio_output: dict[str, object],
    ) -> dict[str, object]:
        result_text = str(provider_output.get("result", "No provider output."))
        return {
            "pipeline": "document",
            "status": "completed",
            "analysis": analysis,
            "summary": "Documentation draft generated.",
            "explanation": result_text,
            "steps": [
                {"title": "Review generated sections", "detail": "Validate README and API sections."},
                {"title": "Apply repository specifics", "detail": "Adjust setup commands and env vars."},
            ],
            "references": [],
            "next_actions": [
                {"label": "Refine generated docs", "action_type": "refine"},
                {"label": "Create changelog", "action_type": "create_doc"},
            ],
            "output_type": studio_output.get("output_type", "README"),
            "content": studio_output.get("content", {}),
            "theme": studio_output.get("theme", {}),
            "markdown": studio_output.get("markdown", ""),
            "metadata": {"structure": structure},
        }
