class PromptAnalyzer:
    def analyze(self, raw_prompt: str) -> dict[str, object]:
        text = raw_prompt.lower().strip()

        weak_areas: list[str] = []
        improvements_applied: list[str] = []

        has_constraints = "constraint" in text or "must" in text
        has_context = "project" in text or "context" in text
        has_output_format = "output format" in text or "format" in text
        has_structure = "folder" in text or "structure" in text

        if not has_constraints:
            weak_areas.append("Missing Constraints")
            improvements_applied.append("Added Constraints")
        if not has_context:
            weak_areas.append("Missing Context")
            improvements_applied.append("Added Context")
        if not has_output_format:
            weak_areas.append("No Output Format")
            improvements_applied.append("Added Expected Output")
        if not has_structure:
            weak_areas.append("Missing Project Structure")
            improvements_applied.append("Added Architecture")

        if len(text.split()) <= 6 and "fastapi" not in text and "django" not in text and "express" not in text and "spring" not in text:
            return {
                "score": 52,
                "weak_areas": weak_areas or ["Missing Context"],
                "improvements_applied": improvements_applied,
                "clarification_needed": True,
                "follow_up_question": {
                    "id": "framework",
                    "question": "Which framework are you targeting?",
                    "options": ["FastAPI", "Django", "Express", "Spring Boot"],
                },
            }

        score = max(40, 100 - (len(weak_areas) * 9))
        return {
            "score": score,
            "weak_areas": weak_areas,
            "improvements_applied": improvements_applied,
            "clarification_needed": False,
        }
