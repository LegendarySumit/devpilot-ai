from typing import Optional, Dict, Any, List
import re
from app.services.context_extractor_base import ContextExtractor, ExtractionMetadata
from app.models.canonical_project_model import (
    CanonicalProjectModel,
    Identity,
    Purpose,
    Feature,
    Installation,
    InstallationMethod,
    Usage,
    Example,
    Community,
    License,
    Status,
)


class ReadmeContextExtractor(ContextExtractor):
    """Extracts context from an existing README.md file"""
    
    def extract(self, input_data: str) -> tuple[CanonicalProjectModel, ExtractionMetadata]:
        """
        Extract project context from README content
        
        Args:
            input_data: Markdown content of README.md
            
        Returns:
            Tuple of (CanonicalProjectModel, ExtractionMetadata)
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input for README extraction")
        
        self.metadata = ExtractionMetadata()
        self.metadata['extraction_method'] = "existing_readme"
        self.readme_content = input_data
        self.sections = self._parse_sections(input_data)
        
        # Extract components
        identity = self._extract_identity()
        purpose = self._extract_purpose()
        features = self._extract_features()
        installation = self._extract_installation()
        usage = self._extract_usage()
        community = self._extract_community()
        status = self._extract_status()
        
        # Quality analysis
        quality_analysis = self._analyze_quality()
        
        # Calculate confidence
        filled = sum([
            bool(identity.name),
            bool(purpose),
            bool(features),
            bool(installation),
            bool(community),
        ])
        self.metadata['confidence_score'] = self._calculate_confidence(filled, 5)
        self.metadata['quality_analysis'] = quality_analysis
        
        cpm = CanonicalProjectModel(
            source="existing_readme",
            identity=identity,
            purpose=purpose,
            features=features,
            installation=installation,
            usage=usage,
            community=community,
            status=status,
        )
        
        return cpm, self.metadata
    
    def validate_input(self, input_data: str) -> bool:
        """Validate if input is markdown content"""
        return isinstance(input_data, str) and len(input_data.strip()) > 50
    
    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse README into sections by heading"""
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('##'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                
                # Extract section title
                current_section = line.replace('#', '').strip().lower().replace(' ', '_')
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_identity(self) -> Identity:
        """Extract identity from README"""
        # Get title from first H1
        match = re.search(r'^#\s+(.+)$', self.readme_content, re.MULTILINE)
        name = match.group(1).strip() if match else "Untitled Project"
        
        # Get description from first paragraph after title
        lines = self.readme_content.split('\n')
        description = ""
        
        for i, line in enumerate(lines):
            if line.startswith('#') and name in line:
                # Look for first non-empty, non-heading line after title
                for next_line in lines[i+1:i+10]:
                    if next_line.strip() and not next_line.startswith('#'):
                        description = next_line.strip()
                        break
                break
        
        self.metadata['fields_with_high_confidence'].append('identity.name')
        
        return Identity(
            name=name,
            slug=name.lower().replace(' ', '-'),
            short_description=description[:200] if description else name,
            full_description=description,
        )
    
    def _extract_purpose(self) -> Optional[Purpose]:
        """Extract purpose from intro section"""
        intro = self.sections.get('intro', '')
        
        problem = None
        for line in intro.split('\n')[:5]:
            if any(word in line.lower() for word in ['solves', 'helps', 'enables', 'for']):
                problem = line.strip()
                break
        
        if problem:
            self.metadata['fields_with_medium_confidence'].append('purpose')
        
        return Purpose(problem_solved=problem)
    
    def _extract_features(self) -> List[Feature]:
        """Extract features from features section"""
        features = []
        
        # Look for features section
        for section_name, content in self.sections.items():
            if 'feature' in section_name or 'highlight' in section_name:
                # Parse bullet points
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('*'):
                        feature_text = line.lstrip('-*').strip()
                        # Split by colon if present (Name: Description)
                        if ':' in feature_text:
                            name, desc = feature_text.split(':', 1)
                            features.append(Feature(name=name.strip(), description=desc.strip()))
                        else:
                            features.append(Feature(name=feature_text))
        
        if features:
            self.metadata['fields_with_high_confidence'].append('features')
        
        return features[:10]
    
    def _extract_installation(self) -> Optional[Installation]:
        """Extract installation instructions"""
        installation_methods = []
        
        for section_name, content in self.sections.items():
            if 'install' in section_name or 'setup' in section_name:
                # Try to find install commands
                code_blocks = re.findall(r'```(?:bash|shell)?\n(.*?)\n```', content, re.DOTALL)
                
                for code in code_blocks:
                    lines = code.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        # Detect package managers
                        if line.startswith('npm'):
                            installation_methods.append(InstallationMethod(
                                method="npm",
                                command=line,
                            ))
                        elif line.startswith('pip'):
                            installation_methods.append(InstallationMethod(
                                method="pip",
                                command=line,
                            ))
                        elif line.startswith('yarn'):
                            installation_methods.append(InstallationMethod(
                                method="yarn",
                                command=line,
                            ))
                        elif line.startswith('cargo'):
                            installation_methods.append(InstallationMethod(
                                method="cargo",
                                command=line,
                            ))
        
        if installation_methods:
            self.metadata['fields_with_high_confidence'].append('installation')
            return Installation(installation_methods=installation_methods)
        
        return None
    
    def _extract_usage(self) -> Optional[Usage]:
        """Extract usage examples"""
        examples = []
        
        for section_name, content in self.sections.items():
            if any(word in section_name for word in ['usage', 'quick_start', 'example']):
                # Extract code blocks
                code_blocks = re.findall(r'```(?:(\w+))?\n(.*?)\n```', content, re.DOTALL)
                
                for language, code in code_blocks:
                    examples.append(Example(
                        title=f"{language or 'Code'} Example",
                        code=code.strip(),
                        language=language or 'plaintext',
                    ))
        
        if examples:
            self.metadata['fields_with_medium_confidence'].append('usage')
            return Usage(examples=examples)
        
        return None
    
    def _extract_community(self) -> Community:
        """Extract community information"""
        license_obj = None
        
        for section_name, content in self.sections.items():
            if 'license' in section_name:
                # Try to extract license type
                for line in content.split('\n'):
                    line = line.strip()
                    if any(lic in line for lic in ['MIT', 'Apache', 'GPL', 'BSD', 'ISC']):
                        license_obj = License(type=line)
                        break
                
                if license_obj:
                    self.metadata['fields_with_high_confidence'].append('community.license')
        
        return Community(license=license_obj)
    
    def _extract_status(self) -> Optional[Status]:
        """Extract status from README"""
        # Look for version badges or mentions
        version_match = re.search(r'v?(\d+\.\d+\.\d+)', self.readme_content)
        version = version_match.group(1) if version_match else None
        
        return Status(version=version, active_development=True)
    
    def _analyze_quality(self) -> Dict[str, Any]:
        """Analyze README quality and identify missing sections"""
        expected_sections = [
            'description',
            'features',
            'installation',
            'usage',
            'contributing',
            'license',
        ]
        
        missing_sections = []
        for section in expected_sections:
            if section not in self.sections:
                missing_sections.append(section.title())
        
        score = max(0, 100 - (len(missing_sections) * 15))
        
        return {
            'score': score,
            'missing_sections': missing_sections,
            'extraction_confidence': 'high' if score > 70 else 'medium' if score > 50 else 'low',
        }
