from typing import Optional
from app.services.context_extractor_base import ContextExtractor, ExtractionMetadata
from app.models.canonical_project_model import (
    CanonicalProjectModel,
    Identity,
    Purpose,
    TechnicalStack,
    Feature,
    Status,
)
import re


class IdeaContextExtractor(ContextExtractor):
    """Extracts context from a project idea description"""
    
    def extract(self, input_data: str) -> tuple[CanonicalProjectModel, ExtractionMetadata]:
        """
        Extract project context from a natural language idea
        
        Args:
            input_data: Natural language description of project idea
            
        Returns:
            Tuple of (CanonicalProjectModel, ExtractionMetadata)
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input for idea extraction")
        
        self.metadata = ExtractionMetadata()
        self.metadata['extraction_method'] = "project_idea"
        
        text = input_data.strip()
        
        # Extract components
        name = self._extract_name(text)
        short_desc = self._extract_description(text)
        problem = self._extract_problem(text)
        audience = self._extract_audience(text)
        tech_stack = self._extract_tech_stack(text)
        features = self._extract_features(text)
        
        # Create identity
        if name:
            self.metadata['fields_with_high_confidence'].append('name')
        else:
            self.metadata['fields_requiring_clarification'].append('name')
            self._add_clarification_question('name', 'What is the official project name?')
        
        identity = Identity(
            name=name or "Unnamed Project",
            short_description=short_desc,
        )
        
        # Create purpose
        purpose = Purpose(
            problem_solved=problem,
            target_audience=audience,
            use_cases=features,
        )
        
        # Create technical stack
        tech = None
        if tech_stack:
            tech = TechnicalStack(
                primary_language=tech_stack.get('language'),
                framework=tech_stack.get('framework'),
                dependencies=[],
            )
            self.metadata['fields_with_medium_confidence'].append('technical_stack')
        
        # Create features
        feature_list = [Feature(name=f, description=None) for f in features]
        
        # Create status
        status = Status(
            maturity="idea",
            active_development=True,
        )
        
        # Calculate confidence
        filled = sum([
            bool(name),
            bool(short_desc),
            bool(problem),
            bool(audience),
            bool(tech_stack),
            bool(features),
        ])
        self.metadata['confidence_score'] = self._calculate_confidence(filled, 6)
        
        cpm = CanonicalProjectModel(
            source="project_idea",
            identity=identity,
            purpose=purpose,
            technical_stack=tech,
            features=feature_list,
            status=status,
        )
        
        return cpm, self.metadata
    
    def validate_input(self, input_data: str) -> bool:
        """Validate if input is a non-empty string"""
        return isinstance(input_data, str) and len(input_data.strip()) > 10
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Try to extract project name from first few words"""
        words = text.split()
        if len(words) >= 2:
            # Return first 2-3 words as potential name
            potential_name = " ".join(words[:3])
            if len(potential_name) < 50:
                return potential_name
        return None
    
    def _extract_description(self, text: str) -> str:
        """Extract short description (first sentence)"""
        sentences = text.split('.')
        if sentences:
            desc = sentences[0].strip()
            return desc[:200] if len(desc) > 200 else desc
        return text[:200]
    
    def _extract_problem(self, text: str) -> Optional[str]:
        """Try to extract problem statement"""
        # Look for keywords
        problem_keywords = ["helps", "solves", "enables", "allows", "provides"]
        for keyword in problem_keywords:
            if keyword in text.lower():
                idx = text.lower().find(keyword)
                end_idx = text.find(".", idx)
                if end_idx > idx:
                    return text[idx:end_idx].strip()
        return None
    
    def _extract_audience(self, text: str) -> list[str]:
        """Extract target audience"""
        audience = []
        audience_keywords = {
            "developer": ["developers", "dev", "engineer", "programmer"],
            "data scientist": ["data scientist", "data analyst", "ml engineer"],
            "devops": ["devops", "sre", "infrastructure"],
            "designer": ["designer", "ux", "ui"],
            "business": ["business", "manager", "executive"],
            "team": ["team", "teams", "collaboration"],
        }
        
        text_lower = text.lower()
        for category, keywords in audience_keywords.items():
            if any(kw in text_lower for kw in keywords):
                audience.append(category)
        
        return audience
    
    def _extract_tech_stack(self, text: str) -> Optional[dict]:
        """Extract mentioned technologies"""
        tech = {}
        
        # Languages
        languages = {
            "python": ["python", "py"],
            "javascript": ["javascript", "js", "node"],
            "rust": ["rust"],
            "go": ["golang", "go"],
            "java": ["java"],
            "typescript": ["typescript", "ts"],
        }
        
        # Frameworks
        frameworks = {
            "fastapi": ["fastapi"],
            "react": ["react"],
            "django": ["django"],
            "flask": ["flask"],
            "next": ["next.js", "nextjs"],
            "express": ["express"],
            "vue": ["vue"],
            "angular": ["angular"],
        }
        
        text_lower = text.lower()
        
        for lang, keywords in languages.items():
            if any(kw in text_lower for kw in keywords):
                tech['language'] = lang
                break
        
        for framework, keywords in frameworks.items():
            if any(kw in text_lower for kw in keywords):
                tech['framework'] = framework
                break
        
        return tech if tech else None
    
    def _extract_features(self, text: str) -> list[str]:
        """Extract mentioned features"""
        features = []
        
        # Look for feature indicators
        feature_text = text
        
        # Common feature patterns
        patterns = [
            r"(?:can|allows?|enables?|provides?)\s+(?:users?\s+)?to\s+([^,.]+)",
            r"(?:supports?|includes?)\s+([^,.]+)",
        ]
        
        for pattern in patterns:
            import re
            matches = re.findall(pattern, feature_text, re.IGNORECASE)
            features.extend([m.strip() for m in matches if m.strip()])
        
        # Also try to extract any action verbs + objects
        action_verbs = ["track", "manage", "generate", "analyze", "optimize", "visualize"]
        for verb in action_verbs:
            if verb in text_lower := text.lower():
                idx = text_lower.find(verb)
                snippet = text[idx:idx + 50]
                features.append(snippet.split(',')[0].split('.')[0].strip())
        
        return list(set(features))[:5]  # Return max 5 unique features
