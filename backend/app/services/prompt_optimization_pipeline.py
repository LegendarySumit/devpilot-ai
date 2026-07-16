from app.services.llm_enhancer import LLMEnhancer
from app.services.prompt_analyzer import PromptAnalyzer
from app.services.prompt_optimizer import PromptOptimizer


class PromptOptimizationPipeline:
    def __init__(self) -> None:
        self.analyzer = PromptAnalyzer()
        self.optimizer = PromptOptimizer()
        self.llm_enhancer = LLMEnhancer()

    def run(self, artifact: str) -> dict[str, object]:
        analysis = self.analyzer.analyze(artifact)

        if analysis.get("clarification_needed"):
            return {
                "pipeline": "build",
                "status": "needs_clarification",
                "analysis": analysis,
                "follow_up_question": analysis.get("follow_up_question"),
                "next_actions": [
                    {
                        "label": "Answer follow-up question",
                        "action_type": "refine",
                    }
                ],
            }

        optimized_prompt = self.optimizer.optimize(artifact, analysis)
        enhanced_prompt = self.llm_enhancer.enhance(optimized_prompt, analysis)

        return {
            "pipeline": "build",
            "status": "completed",
            "analysis": {
                "score": analysis["score"],
                "weak_areas": analysis["weak_areas"],
                "improvements_applied": analysis["improvements_applied"],
            },
            "optimized_prompt": enhanced_prompt,
            "why_it_is_better": [
                "More explicit task context",
                "Clear constraints reduce ambiguous outputs",
                "Defined output format improves downstream usability",
            ],
            "next_actions": [
                {"label": "Copy optimized prompt", "action_type": "copy"},
                {"label": "Refine for target model", "action_type": "refine"},
            ],
        }
