"""
Debug LLM Enhancer - Integrates LLM for advanced reasoning and explanations
Uses LLM service abstraction to support multiple providers (Gemini, Mistral, etc.)
"""
import json
import re
from .debug_models import (
    RootCauseAnalysis,
    Solution,
    LearningContent,
    DebugStrategy,
    AnalysisMetadata,
)


class DebugLLMEnhancer:
    """
    Enhances debug analysis with LLM-powered reasoning
    
    Responsibilities:
    - Root cause reasoning (why did this happen?)
    - Solution generation (how to fix it?)
    - Educational content (what to learn?)
    - Code examples (wrong vs correct)
    """
    
    def __init__(self, llm_service=None):
        """
        Initialize with LLM service
        Automatically loads from app.services.llm if not provided
        """
        self.llm_service = llm_service
        
        if self.llm_service is None:
            try:
                from app.services.llm import LLMService
                self.llm_service = LLMService()
            except (ImportError, ModuleNotFoundError) as e:
                print(f"Warning: LLMService not available: {e}")
                self.llm_service = None
    
    def enhance_root_cause(
        self,
        metadata: AnalysisMetadata,
        strategy: DebugStrategy,
        error_content: str,
    ) -> RootCauseAnalysis:
        """
        Use LLM to provide deeper root cause analysis
        Falls back to rule-based if LLM unavailable
        """
        
        if not self.llm_service:
            return self._generate_rule_based_root_cause(metadata, strategy, error_content)
        
        try:
            prompt = self._build_root_cause_prompt(metadata, strategy, error_content)
            llm_response = self.llm_service.generate(
                prompt=prompt,
                model=None,  # Use default model
                temperature=0.3,  # Low temperature for factual root cause analysis
            )
            return self._parse_llm_root_cause(llm_response, metadata)
        except Exception as e:
            print(f"LLM enhancement failed for root cause: {e}")
            return self._generate_rule_based_root_cause(metadata, strategy, error_content)
    
    def enhance_solution(
        self,
        metadata: AnalysisMetadata,
        strategy: DebugStrategy,
        error_content: str,
    ) -> Solution:
        """
        Use LLM to generate detailed solution steps
        Falls back to rule-based if LLM unavailable
        """
        
        if not self.llm_service:
            return self._generate_rule_based_solution(metadata, strategy, error_content)
        
        try:
            prompt = self._build_solution_prompt(metadata, strategy, error_content)
            llm_response = self.llm_service.generate(
                prompt=prompt,
                model=None,  # Use default model
                temperature=0.2,  # Very low temperature for accurate solution steps
            )
            return self._parse_llm_solution(llm_response, metadata)
        except Exception as e:
            print(f"LLM enhancement failed for solution: {e}")
            return self._generate_rule_based_solution(metadata, strategy, error_content)
    
    def enhance_learning(
        self,
        metadata: AnalysisMetadata,
        strategy: DebugStrategy,
        error_content: str,
    ) -> LearningContent:
        """
        Use LLM to generate educational content
        Falls back to rule-based if LLM unavailable
        """
        
        if not self.llm_service:
            return self._generate_rule_based_learning(metadata, strategy, error_content)
        
        try:
            prompt = self._build_learning_prompt(metadata, strategy, error_content)
            llm_response = self.llm_service.generate(
                prompt=prompt,
                model=None,  # Use default model
                temperature=0.5,  # Moderate temperature for educational content
            )
            return self._parse_llm_learning(llm_response, metadata)
        except Exception as e:
            print(f"LLM enhancement failed for learning: {e}")
            return self._generate_rule_based_learning(metadata, strategy, error_content)
    
    # ========================================================================
    # PROMPT BUILDING
    # ========================================================================
    
    def _build_root_cause_prompt(
        self,
        metadata: AnalysisMetadata,
        strategy: DebugStrategy,
        error_content: str,
    ) -> str:
        """Build prompt for root cause analysis"""
        
        focus_areas = "\n".join(f"- {area}" for area in strategy.focus_areas)
        likely_causes = "\n".join(f"- {cause}" for cause in strategy.likely_causes)
        
        return f"""You are an expert {metadata.language} debugger. Analyze this error VERY CAREFULLY and provide the EXACT root cause.

**CRITICAL: Read the error message literally. Do NOT generalize.**

**Error Information:**
Language: {metadata.language}
Framework: {metadata.framework or 'Unknown'}
Error Category: {metadata.category}
Error Severity: {metadata.severity}

**THE ACTUAL ERROR (read this carefully):**
{error_content}

**What to focus on (specific areas for this error):**
{focus_areas}

**Likely specific causes:**
{likely_causes}

**IMPORTANT:** 
- If it says "cannot import name X from Y", the root cause is that X was moved or removed from Y
- If it says "ModuleNotFoundError", the root cause is the package is not installed
- Be SPECIFIC - not generic. Use exact error message details in your analysis.

**Response MUST be valid JSON only (no markdown, no extra text):**
{{
    "summary": "Exact one-sentence summary of what went wrong (be specific, not generic)",
    "root_cause": "The SPECIFIC root cause based on the exact error message",
    "why_it_happened": "Explain WHY this specific thing happened based on the error details",
    "contributing_factors": ["specific factor 1", "specific factor 2"],
    "confidence": 0.95
}}
"""
    
    def _build_solution_prompt(
        self,
        metadata: AnalysisMetadata,
        strategy: DebugStrategy,
        error_content: str,
    ) -> str:
        """Build prompt for solution generation"""
        
        focus_areas = "\n".join(f"- {area}" for area in strategy.focus_areas)
        
        return f"""You are an expert {metadata.language} developer. Generate step-by-step solutions to fix this error.

**Error Information:**
Language: {metadata.language}
Framework: {metadata.framework or 'Unknown'}
Category: {metadata.category}

**Error Content:**
{error_content}

**What to focus on:**
{focus_areas}

**Your response MUST be valid JSON only (no markdown, no extra text):**
{{
    "steps": [
        "Step 1: description",
        "Step 2: description",
        "Step 3: description"
    ],
    "corrected_code": "Show corrected code example here",
    "corrected_config": "Show corrected configuration if applicable",
    "dependencies_to_add": ["package1", "package2"],
    "commands_to_run": ["pip install package", "run test command"]
}}
"""
    
    def _build_learning_prompt(
        self,
        metadata: AnalysisMetadata,
        strategy: DebugStrategy,
        error_content: str,
    ) -> str:
        """Build prompt for learning content generation"""
        
        doc_sections = "\n".join(f"- {section}" for section in strategy.documentation_sections)
        
        return f"""You are an expert educator. Explain this {metadata.language} error to help developers understand and prevent it.

**Error Information:**
Language: {metadata.language}
Framework: {metadata.framework or 'Unknown'}
Category: {metadata.category}

**Error Content:**
{error_content}

**Related Concepts:**
{doc_sections}

**Your response MUST be valid JSON only (no markdown, no extra text):**
{{
    "concept_explained": "What core concept is being violated",
    "common_mistakes": ["mistake1", "mistake2", "mistake3"],
    "prevention_strategies": ["strategy1", "strategy2", "strategy3"],
    "mental_model": "How developers should think about this concept",
    "best_practices": ["practice1", "practice2", "practice3"]
}}
"""
    
    # ========================================================================
    # LLM RESPONSE PARSING
    # ========================================================================
    
    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON string from LLM response, handling markdown code blocks"""
        
        if not content:
            return "{}"
        
        # Remove markdown code blocks
        if '```json' in content:
            try:
                content = content.split('```json')[1].split('```')[0].strip()
            except IndexError:
                pass
        elif '```' in content:
            try:
                content = content.split('```')[1].split('```')[0].strip()
            except IndexError:
                pass
        
        # Find JSON object in content
        content = content.strip()
        if content.startswith('{'):
            # Find the closing brace by tracking depth
            depth = 0
            for i, char in enumerate(content):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        return content[:i+1]
        
        return content
    
    def _safe_json_parse(self, json_str: str) -> dict:
        """Safely parse JSON with comprehensive fallback cleaning"""
        
        # Try direct parse first
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Attempt 1: Clean whitespace but preserve structure
            try:
                # Remove extra spaces but keep newlines inside strings
                cleaned = re.sub(r'\n\s*', ' ', json_str)
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
        
        # Attempt 2: Fix common issues
        try:
            # Fix escaped newlines inside strings
            json_str = json_str.replace('\\n', '\\\\n')
            # Remove any trailing commas
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Attempt 3: Extract just the JSON object/array
        try:
            # Find first { or [ and last } or ]
            start_idx = -1
            end_idx = -1
            
            for i, char in enumerate(json_str):
                if char in '{[':
                    start_idx = i
                    break
            
            for i in range(len(json_str) - 1, -1, -1):
                if json_str[i] in '}]':
                    end_idx = i
                    break
            
            if start_idx >= 0 and end_idx > start_idx:
                extracted = json_str[start_idx:end_idx+1]
                return json.loads(extracted)
        except json.JSONDecodeError:
            pass
        
        # Last resort: return empty dict with error message
        return {
            "error": "Failed to parse LLM JSON response",
            "raw_response": json_str[:200]
        }
    
    def _parse_llm_root_cause(
        self,
        llm_response,
        metadata: AnalysisMetadata,
    ) -> RootCauseAnalysis:
        """Parse LLM response into RootCauseAnalysis"""
        
        try:
            # Handle both dict and LLMResponse object
            if hasattr(llm_response, 'content'):
                content = llm_response.content
            else:
                content = llm_response.get("content", "")
            
            if not content or not isinstance(content, str):
                raise ValueError(f"Invalid content type: {type(content)}")
            
            # Extract JSON from response
            json_str = self._extract_json_from_response(content)
            parsed = self._safe_json_parse(json_str)
            
            # Validate we got useful data
            if "error" in parsed and len(parsed) < 3:
                print("LLM returned error/empty response, using fallback")
                return self._generate_rule_based_root_cause(metadata, None, "")
            
            return RootCauseAnalysis(
                summary=parsed.get("summary", "Unknown error"),
                root_cause=parsed.get("root_cause", "Unable to determine"),
                why_it_happened=parsed.get("why_it_happened", "Analysis unavailable"),
                contributing_factors=parsed.get("contributing_factors", []),
                confidence=float(parsed.get("confidence", 0.5)),
            )
        except Exception as e:
            print(f"LLM root cause parsing failed: {e}. Using fallback.")
            return self._generate_rule_based_root_cause(metadata, None, "")
    
    def _parse_llm_solution(
        self,
        llm_response,
        metadata: AnalysisMetadata,
    ) -> Solution:
        """Parse LLM response into Solution"""
        
        try:
            # Handle both dict and LLMResponse object
            if hasattr(llm_response, 'content'):
                content = llm_response.content
            else:
                content = llm_response.get("content", "")
            
            if not content or not isinstance(content, str):
                raise ValueError(f"Invalid content type: {type(content)}")
            
            # Extract JSON from response
            json_str = self._extract_json_from_response(content)
            parsed = self._safe_json_parse(json_str)
            
            # Validate we got useful data
            if "error" in parsed and len(parsed) < 3:
                print("LLM returned error/empty response for solution, using fallback")
                return self._generate_rule_based_solution(metadata, None, "")
            
            return Solution(
                steps=parsed.get("steps", []),
                corrected_code=parsed.get("corrected_code"),
                corrected_config=parsed.get("corrected_config"),
                dependencies_to_add=parsed.get("dependencies_to_add", []),
                commands_to_run=parsed.get("commands_to_run", []),
            )
        except Exception as e:
            print(f"LLM solution parsing failed: {e}. Using fallback.")
            return self._generate_rule_based_solution(metadata, None, "")
    
    def _parse_llm_learning(
        self,
        llm_response,
        metadata: AnalysisMetadata,
    ) -> LearningContent:
        """Parse LLM response into LearningContent"""
        
        try:
            # Handle both dict and LLMResponse object
            if hasattr(llm_response, 'content'):
                content = llm_response.content
            else:
                content = llm_response.get("content", "")
            
            if not content or not isinstance(content, str):
                raise ValueError(f"Invalid content type: {type(content)}")
            
            # Extract JSON from response
            json_str = self._extract_json_from_response(content)
            parsed = self._safe_json_parse(json_str)
            
            # Validate we got useful data
            if "error" in parsed and len(parsed) < 3:
                print("LLM returned error/empty response for learning, using fallback")
                return self._generate_rule_based_learning(metadata, None, "")
            
            return LearningContent(
                concept_explained=parsed.get("concept_explained", ""),
                common_mistakes=parsed.get("common_mistakes", []),
                prevention_strategies=parsed.get("prevention_strategies", []),
                mental_model=parsed.get("mental_model"),
                best_practices=parsed.get("best_practices", []),
            )
        except Exception as e:
            print(f"LLM learning parsing failed: {e}. Using fallback.")
            return self._generate_rule_based_learning(metadata, None, "")
    
    # ========================================================================
    # RULE-BASED FALLBACKS
    # ========================================================================
    
    def _generate_rule_based_root_cause(
        self,
        metadata: AnalysisMetadata,
        strategy,
        error_content: str,
    ) -> RootCauseAnalysis:
        """Generate root cause using rules when LLM unavailable"""
        
        return RootCauseAnalysis(
            summary=f"{metadata.category.replace('_', ' ').title()} in {metadata.language}",
            root_cause="Unable to analyze - LLM service unavailable",
            why_it_happened="The LLM enhancement service is not available. Using fallback analysis.",
            contributing_factors=[],
            confidence=0.0,
        )
    
    def _generate_rule_based_solution(
        self,
        metadata: AnalysisMetadata,
        strategy,
        error_content: str,
    ) -> Solution:
        """Generate solution using rules when LLM unavailable"""
        
        return Solution(
            steps=[
                "Enable LLM service for specific solutions",
                "Review the error message carefully",
                "Check the relevant documentation",
                "Verify your configuration and environment",
            ],
            corrected_code=None,
            corrected_config=None,
            dependencies_to_add=[],
            commands_to_run=[],
        )
    
    def _generate_rule_based_learning(
        self,
        metadata: AnalysisMetadata,
        strategy,
        error_content: str,
    ) -> LearningContent:
        """Generate learning content using rules when LLM unavailable"""
        
        return LearningContent(
            concept_explained=f"Error category: {metadata.category}",
            common_mistakes=[
                "Not reading error messages carefully",
                "Skipping documentation",
                "Configuration issues",
            ],
            prevention_strategies=[
                "Enable LLM service for better error analysis",
                "Write tests to catch errors early",
                "Keep dependencies updated",
            ],
            mental_model="Errors are feedback from the system about what went wrong",
            best_practices=[
                "Always read the full error message",
                "Check documentation for your framework",
                "Use version control to track changes",
            ],
        )
