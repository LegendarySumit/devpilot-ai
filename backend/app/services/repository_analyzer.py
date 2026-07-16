from app.services.analysis_contract import AnalysisContract


class RepositoryAnalyzer:
    def analyze(self, raw_repository_input: str) -> dict[str, object]:
        normalized = raw_repository_input.lower().strip()
        issues: list[str] = []

        if "github.com" not in normalized:
            issues.append("Input may not be a valid GitHub repository URL")
        if normalized.endswith("/"):
            issues.append("Repository URL has trailing slash; normalize for fetch reliability")

        return AnalysisContract.build(
            analysis_type="repository",
            confidence=0.95 if "github.com" in normalized else 0.72,
            summary="Repository input analyzed for documentation generation readiness.",
            issues=issues,
            metadata={"source": "github" if "github.com" in normalized else "unknown"},
        )
