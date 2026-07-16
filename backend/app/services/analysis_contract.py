from typing import Any


class AnalysisContract:
    @staticmethod
    def build(
        analysis_type: str,
        confidence: float,
        summary: str,
        issues: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "type": analysis_type,
            "confidence": max(0.0, min(confidence, 1.0)),
            "summary": summary,
            "issues": issues or [],
            "metadata": metadata or {},
        }
