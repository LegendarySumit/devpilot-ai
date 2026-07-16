from app.services.analysis_contract import AnalysisContract


class ErrorAnalyzer:
    def analyze(self, raw_error: str) -> dict[str, object]:
        normalized = raw_error.lower()
        issues: list[str] = []

        if "keyerror" in normalized:
            issues.append("Likely missing dictionary key access guard")
        if "none" in normalized and "type" in normalized:
            issues.append("Potential null/None dereference")
        if "traceback" not in normalized:
            issues.append("Incomplete traceback context")

        summary = "Error analyzed for likely failure patterns and missing context."
        return AnalysisContract.build(
            analysis_type="error",
            confidence=0.92,
            summary=summary,
            issues=issues,
            metadata={"detected_language": "python" if "traceback" in normalized else "unknown"},
        )
