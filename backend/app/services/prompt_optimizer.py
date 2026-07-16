class PromptOptimizer:
    def optimize(self, raw_prompt: str, analysis: dict[str, object]) -> str:
        base = raw_prompt.strip()

        sections = [
            "You are a senior software engineer.",
            "Task:\n" + base,
            "Constraints:\n- Follow production-safe defaults\n- Keep implementation modular\n- Include edge-case handling",
            "Project Structure Expectations:\n- Show target folders/files\n- Explain where each piece belongs",
            "Output Format:\n1. Plan\n2. File-level changes\n3. Validation checklist",
        ]

        if analysis.get("weak_areas"):
            sections.append("Focus Areas:\n- " + "\n- ".join(str(x) for x in analysis["weak_areas"]))

        return "\n\n".join(sections)
