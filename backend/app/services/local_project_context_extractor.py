from typing import Optional, Dict, Any, List
import json
import re
from app.services.context_extractor_base import ContextExtractor, ExtractionMetadata
from app.models.canonical_project_model import (
    CanonicalProjectModel,
    Identity,
    TechnicalStack,
    Dependency,
    Feature,
    Installation,
    InstallationMethod,
    Community,
    Status,
    Assets,
    Social,
)


class LocalProjectContextExtractor(ContextExtractor):
    """Extracts context from a local project folder"""
    
    def extract(self, input_data: Dict[str, Any]) -> tuple[CanonicalProjectModel, ExtractionMetadata]:
        """Extract project context from local folder"""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input for local project extraction")
        
        self.metadata = ExtractionMetadata()
        self.metadata['extraction_method'] = "local_project"
        self.files = input_data.get('files', {})
        
        identity = self._extract_identity(input_data)
        tech_stack = self._extract_tech_stack()
        features = self._extract_features()
        installation = self._extract_installation()
        community = self._extract_community()
        assets = self._extract_assets()
        status = self._extract_status()
        
        filled = sum([bool(identity.name), bool(tech_stack), bool(installation), bool(community)])
        self.metadata['confidence_score'] = self._calculate_confidence(filled, 4)
        
        cpm = CanonicalProjectModel(
            source="local_project",
            identity=identity,
            technical_stack=tech_stack,
            features=features,
            installation=installation,
            community=community,
            assets=assets,
            status=status,
        )
        
        return cpm, self.metadata
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate if input has required keys"""
        return isinstance(input_data, dict) and ('path' in input_data or 'files' in input_data)
    
    def _extract_identity(self, input_data: Dict) -> Identity:
        """Extract identity from folder structure and files"""
        name = input_data.get('project_name', 'Project')
        description = ""
        
        if 'package.json' in self.files:
            try:
                pkg = json.loads(self.files['package.json'])
                name = pkg.get('name', name)
                description = pkg.get('description', '')
            except:
                pass
        
        if 'README.md' in self.files:
            lines = self.files['README.md'].split('\n')
            for line in lines[:5]:
                if line.startswith('#') and not line.startswith('##'):
                    name = line.replace('#', '').strip()
                elif not line.startswith('#') and line.strip() and not description:
                    description = line.strip()
        
        self.metadata['fields_with_high_confidence'].append('identity')
        
        return Identity(
            name=name,
            slug=name.lower().replace(' ', '-'),
            short_description=description[:200] if description else name,
        )
    
    def _extract_tech_stack(self) -> Optional[TechnicalStack]:
        """Detect tech stack from dependency files"""
        primary_language = self._detect_language()
        framework = None
        dependencies = []
        
        if 'package.json' in self.files:
            try:
                pkg = json.loads(self.files['package.json'])
                framework = self._detect_npm_framework(pkg)
                for name, version in pkg.get('dependencies', {}).items():
                    dependencies.append(Dependency(name=name, version=version))
                self.metadata['fields_with_high_confidence'].append('technical_stack')
            except:
                pass
        
        if 'requirements.txt' in self.files:
            if not framework:
                framework = self._detect_python_framework(self.files['requirements.txt'])
            deps = self._parse_requirements(self.files['requirements.txt'])
            for dep in deps:
                dependencies.append(Dependency(name=dep['name'], version=dep.get('version')))
            self.metadata['fields_with_medium_confidence'].append('technical_stack')
        
        if 'Cargo.toml' in self.files:
            if not framework:
                framework = "Rust"
            self.metadata['fields_with_medium_confidence'].append('technical_stack')
        
        if 'go.mod' in self.files:
            if not framework:
                framework = "Go"
            self.metadata['fields_with_medium_confidence'].append('technical_stack')
        
        if primary_language or framework or dependencies:
            return TechnicalStack(
                primary_language=primary_language,
                framework=framework,
                dependencies=dependencies[:10],
            )
        
        return None
    
    def _extract_features(self) -> List[Feature]:
        """Extract features from README"""
        features = []
        
        if 'README.md' not in self.files:
            return features
        
        content = self.files['README.md']
        lines = content.split('\n')
        in_features = False
        
        for line in lines:
            if '## features' in line.lower() or '## key features' in line.lower():
                in_features = True
                continue
            
            if in_features and line.startswith('##'):
                break
            
            if in_features and (line.startswith('-') or line.startswith('*')):
                feature_text = line.strip().lstrip('-*').strip()
                if feature_text:
                    features.append(Feature(name=feature_text))
        
        return features[:10]
    
    def _extract_installation(self) -> Optional[Installation]:
        """Detect installation methods"""
        methods = []
        
        if 'package.json' in self.files:
            try:
                pkg = json.loads(self.files['package.json'])
                name = pkg.get('name', 'package')
                methods.append(InstallationMethod(
                    method="npm",
                    command=f"npm install {name}",
                ))
            except:
                pass
        
        if 'requirements.txt' in self.files:
            methods.append(InstallationMethod(
                method="pip",
                command="pip install -r requirements.txt",
            ))
        
        if 'Cargo.toml' in self.files:
            methods.append(InstallationMethod(
                method="cargo",
                command="cargo build",
            ))
        
        if 'go.mod' in self.files:
            methods.append(InstallationMethod(
                method="go",
                command="go build",
            ))
        
        if methods:
            self.metadata['fields_with_high_confidence'].append('installation')
            return Installation(installation_methods=methods)
        
        return None
    
    def _extract_community(self) -> Community:
        """Extract community info"""
        return Community()
    
    def _extract_assets(self) -> Optional[Assets]:
        """Extract assets"""
        return None
    
    def _extract_status(self) -> Status:
        """Extract status"""
        return Status(active_development=True)
    
    def _detect_language(self) -> Optional[str]:
        """Detect primary language from files"""
        if 'package.json' in self.files:
            return "JavaScript"
        if 'requirements.txt' in self.files or 'setup.py' in self.files:
            return "Python"
        if 'Cargo.toml' in self.files:
            return "Rust"
        if 'go.mod' in self.files:
            return "Go"
        if 'pom.xml' in self.files:
            return "Java"
        return None
    
    def _detect_npm_framework(self, pkg: dict) -> Optional[str]:
        """Detect framework from package.json"""
        deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
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
            match = re.match(r'^([a-zA-Z0-9\-_]+)(?:([><=!]+)(.+))?', line)
            if match:
                name = match.group(1)
                version = match.group(3) if match.group(3) else None
                deps.append({'name': name, 'version': version})
        return deps
