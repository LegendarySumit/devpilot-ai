class ClassifierService:
    def classify(self, artifact: str) -> dict[str, object]:
        normalized = artifact.lower().strip()
        if "traceback" in normalized or "error" in normalized or "exception" in normalized:
            return {
                "artifact_type": "python_traceback",
                "pipeline": "debug",
                "confidence": 0.98,
                "reasons": ["traceback/error signature detected"],
            }
        if "github.com" in normalized or "readme" in normalized or "documentation" in normalized:
            return {
                "artifact_type": "github_repository",
                "pipeline": "document",
                "confidence": 1.0,
                "reasons": ["repository or docs keyword detected"],
            }
        return {
            "artifact_type": "prompt",
            "pipeline": "build",
            "confidence": 0.91,
            "reasons": ["defaulted to prompt optimization"],
        }
