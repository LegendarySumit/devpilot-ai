from app.services.document_generator import DocumentGenerator
from app.services.documentation_studio_service import DocumentationStudioService
from app.services.llm_service import LLMService
from app.services.repository_analyzer import RepositoryAnalyzer
from app.services.structure_detector import StructureDetector


class DocumentPipeline:
    def __init__(self) -> None:
        self.repository_analyzer = RepositoryAnalyzer()
        self.structure_detector = StructureDetector()
        self.llm_service = LLMService()
        self.documentation_studio = DocumentationStudioService()
        self.document_generator = DocumentGenerator()

    def run(
        self,
        artifact: str,
        theme_name: str = "professional",
        theme_variant: str = "light",
        mode: str = "ai",
    ) -> dict[str, object]:
        analysis = self.repository_analyzer.analyze(artifact)
        structure = self.structure_detector.detect(artifact, analysis)

        studio_output = self.documentation_studio.generate_readme(
            project_context=artifact,
            theme_name=theme_name,
            theme_variant=theme_variant,
            mode=mode,
        )

        prompt = (
            "Enhance documentation quality while preserving structure and readability.\n\n"
            f"README Draft:\n{studio_output['markdown']}"
        )
        provider_output = self.llm_service.generate(prompt)

        return self.document_generator.generate(
            provider_output=provider_output,
            analysis=analysis,
            structure=structure,
            studio_output=studio_output,
        )
