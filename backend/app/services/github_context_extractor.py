from typing import Optional, Dict, Any
import json
import re
from app.services.context_extractor_base import ContextExtractor, ExtractionMetadata
from app.models.canonical_project_model import (
    CanonicalProjectModel,
    Identity,
    Purpose,
    TechnicalStack,
    Dependency,
    Feature,
    Installation,
    InstallationMethod,
    Usage,
    Example,
    Community,
    Maintainer,
    Contributor,
    License,
    ContributionGuidelines,
    Status,
    Assets,
    Social,
)


class GitHubContextExtractor(ContextExtractor):
    """Extracts context from a GitHub repository"""
    
    def extract(self, input_data: Dict[str, Any]) -> tuple[CanonicalProjectModel, ExtractionMetadata]:
        """
        Extract project context from GitHub repository data
        
        Args:
            input_data: Dictionary containing GitHub repo data or URL
            Expected keys:
            - repo_name: Repository name
            - repo_url: Full repository URL
            - owner: Repository owner
            - description: Repository description
            - readme_content: README.md content (optional)
            - package_json: package.json content (optional)
            - requirements_txt: requirements.txt content (optional)
            - languages: Dict of languages and percentages
            - license: License type (optional)
            - topics: List of topics/keywords
            - stars: Star count
            - created_at: Creation date
            - pushed_at: Last push date
            - contributors: List of contributor names
            - has_discussions: Boolean
            
        Returns:
            Tuple of (CanonicalProjectModel, ExtractionMetadata)
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input for GitHub extraction")
        
        self.metadata = ExtractionMetadata()
        self.metadata['extraction_method'] = "github_repository"
        
        # Extract components
        identity = self._extract_identity(input_data)
        purpose = self._extract_purpose(input_data)
        tech_stack = self._extract_tech_stack(input_data)
        features = self._extract_features(input_data)
        installation = self._extract_installation(input_data)
        usage = self._extract_usage(input_data)
        community = self._extract_community(input_data)
        assets = self._extract_assets(input_data)
        status = self._extract_status(input_data)
        
        # Calculate confidence
        filled = sum([
            bool(identity.name),
            bool(purpose),
            bool(tech_stack),
            bool(features),
            bool(community),
            bool(status),
        ])
        self.metadata['confidence_score'] = self._calculate_confidence(filled, 6)
        
        cpm = CanonicalProjectModel(
            source="github_repository",
            identity=identity,
            purpose=purpose,
            technical_stack=tech_stack,
            features=features,
            installation=installation,
            usage=usage,
            community=community,
            assets=assets,
            status=status,
        )
        
        return cpm, self.metadata
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate if input is a valid GitHub repo data dict"""
        if not isinstance(input_data, dict):
            return False
        required_keys = ['repo_name', 'repo_url', 'owner']
        return all(key in input_data for key in required_keys)
    
    def _extract_identity(self, data: Dict) -> Identity:
        """Extract repository identity"""
        name = data.get('repo_name', '')
        description = data.get('description', '')
        
        self.metadata['fields_with_high_confidence'].append('identity')
        
        return Identity(
            name=name,
            slug=name.lower().replace(' ', '-'),
            short_description=description[:200] if description else name,
            full_description=description,
            homepage=data.get('homepage'),
        )
    
    def _extract_purpose(self, data: Dict) -> Purpose:
        """Extract purpose from description and readme"""
        readme_content = data.get('readme_content', '')
        description = data.get('description', '')
        topics = data.get('topics', [])
        
        # Try to extract problem from readme
        problem = None
        if readme_content:
            lines = readme_content.split('\n')
            for i, line in enumerate(lines[:10]):
                if any(word in line.lower() for word in ['solves', 'helps', 'enables', 'problem']):
                    problem = line.strip()
                    break
        
        if problem:
            self.metadata['fields_with_medium_confidence'].append('purpose.problem_solved')
        
        return Purpose(
            problem_solved=problem or description,
            target_audience=[],
            use_cases=[],
        )
    
    def _extract_tech_stack(self, data: Dict) -> Optional[TechnicalStack]:
        """Extract technology stack from package files and language data"""
        languages = data.get('languages', {})
        primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else None
        
        framework = None
        dependencies = []
        
        # Check package.json
        if package_json_str := data.get('package_json'):
            try:
                package_json = json.loads(package_json_str) if isinstance(package_json_str, str) else package_json_str
                framework = self._detect_npm_framework(package_json)
                deps = package_json.get('dependencies', {})
                for name, version in deps.items():
                    dependencies.append(Dependency(name=name, version=version))
                self.metadata['fields_with_high_confidence'].append('technical_stack')
            except:
                pass
        
        # Check requirements.txt
        if requirements := data.get('requirements_txt'):
            if not framework:
                framework = self._detect_python_framework(requirements)
            deps_list = self._parse_requirements(requirements)
            for dep in deps_list:
                dependencies.append(Dependency(name=dep['name'], version=dep.get('version')))
            if not framework:
                self.metadata['fields_with_medium_confidence'].append('technical_stack')
        
        return TechnicalStack(
            primary_language=primary_language,
            framework=framework,
            dependencies=dependencies[:10],  # Limit to top 10
        )
    
    def _extract_features(self, data: Dict) -> list[Feature]:
        """Extract features from readme"""
        readme_content = data.get('readme_content', '')
        features = []
        
        if not readme_content:
            return features
        
        # Look for features section
        lines = readme_content.split('\n')
        in_features = False
        
        for line in lines:
            if '## features' in line.lower() or '## key features' in line.lower():
                in_features = True
                continue
            
            if in_features and line.startswith('##'):
                break
            
            if in_features and line.strip().startswith('-'):
                feature_text = line.strip().lstrip('-').strip()
                if feature_text:
                    features.append(Feature(name=feature_text, description=None))
        
        if features:
            self.metadata['fields_with_high_confidence'].append('features')
        
        return features[:10]  # Limit to 10 features
    
    def _extract_installation(self, data: Dict) -> Optional[Installation]:
        """Extract installation from readme and package files"""
        readme_content = data.get('readme_content', '')
        installation_methods = []
        
        # Detect npm
        if data.get('package_json'):
            installation_methods.append(InstallationMethod(
                method="npm",
                command=f"npm install {data.get('repo_name', '').lower().replace(' ', '-')}",
            ))
        
        # Detect pip
        if data.get('requirements_txt'):
            installation_methods.append(InstallationMethod(
                method="pip",
                command=f"pip install {data.get('repo_name', '').lower().replace(' ', '-')}",
            ))
        
        if installation_methods:
            self.metadata['fields_with_medium_confidence'].append('installation')
        
        return Installation(installation_methods=installation_methods) if installation_methods else None
    
    def _extract_usage(self, data: Dict) -> Optional[Usage]:
        """Extract usage examples from readme"""
        readme_content = data.get('readme_content', '')
        examples = []
        
        if not readme_content:
            return None
        
        # Look for usage/quick start section
        lines = readme_content.split('\n')
        in_usage = False
        code_block = []
        
        for line in lines:
            if any(section in line.lower() for section in ['## usage', '## quick start', '## example']):
                in_usage = True
                continue
            
            if in_usage and line.startswith('##'):
                if code_block:
                    examples.append(Example(
                        title="Example",
                        code='\n'.join(code_block),
                    ))
                break
            
            if in_usage and ('```' in line or code_block):
                if '```' in line:
                    if code_block:
                        examples.append(Example(
                            title="Example",
                            code='\n'.join(code_block),
                        ))
                        code_block = []
                else:
                    code_block.append(line)
        
        return Usage(examples=examples) if examples else None
    
    def _extract_community(self, data: Dict) -> Community:
        """Extract community information"""
        contributors = []
        if contrib_list := data.get('contributors'):
            for name in contrib_list[:5]:  # Top 5
                contributors.append(Contributor(name=name))
        
        license_type = data.get('license', 'Unknown')
        license_obj = License(type=license_type) if license_type else None
        
        maintainer = Maintainer(
            name=data.get('owner', 'Unknown'),
            github=data.get('owner'),
        )
        
        self.metadata['fields_with_high_confidence'].append('community.license')
        self.metadata['fields_with_high_confidence'].append('community.maintainers')
        
        return Community(
            maintainers=[maintainer],
            contributors=contributors,
            license=license_obj,
            contribution_guidelines=ContributionGuidelines(accepting_contributions=True),
        )
    
    def _extract_assets(self, data: Dict) -> Optional[Assets]:
        """Extract asset information"""
        social = Social(
            repository=data.get('repo_url'),
        )
        
        # Detect npm/pypi URLs
        repo_name = data.get('repo_name', '').lower().replace(' ', '-')
        if data.get('package_json'):
            social.npm = f"https://www.npmjs.com/package/{repo_name}"
        
        if data.get('requirements_txt'):
            social.pypi = f"https://pypi.org/project/{repo_name}/"
        
        return Assets(social=social)
    
    def _extract_status(self, data: Dict) -> Status:
        """Extract project status"""
        return Status(
            maturity="stable" if data.get('stars', 0) > 100 else "beta",
            active_development=True,
            last_update=data.get('pushed_at'),
            version=data.get('latest_version'),
        )
    
    def _detect_npm_framework(self, package_json: dict) -> Optional[str]:
        """Detect framework from package.json"""
        deps = {**package_json.get('dependencies', {}), **package_json.get('devDependencies', {})}
        
        frameworks = {
            'react': 'React',
            'vue': 'Vue',
            'angular': 'Angular',
            'next': 'Next.js',
            'nuxt': 'Nuxt',
            'svelte': 'Svelte',
            'express': 'Express',
        }
        
        for dep, name in frameworks.items():
            if dep in deps:
                return name
        
        return None
    
    def _detect_python_framework(self, requirements: str) -> Optional[str]:
        """Detect framework from requirements.txt"""
        frameworks = {
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'tornado': 'Tornado',
            'pyramid': 'Pyramid',
        }
        
        for dep, name in frameworks.items():
            if dep in requirements.lower():
                return name
        
        return None
    
    def _parse_requirements(self, requirements: str) -> list[dict]:
        """Parse requirements.txt into dependencies"""
        deps = []
        for line in requirements.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle various formats: package, package==1.0.0, package>=1.0.0
            match = re.match(r'^([a-zA-Z0-9\-_]+)(?:([><=!]+)(.+))?', line)
            if match:
                name = match.group(1)
                version = match.group(3) if match.group(3) else None
                deps.append({'name': name, 'version': version})
        
        return deps
