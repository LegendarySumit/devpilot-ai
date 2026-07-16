"""
Debug Processor - Generates diagnosis and remediation steps
Incorporates strategy and context enrichment
"""
from typing import Dict, Any, List, Optional, Union
from .debug_models import DebugArtifact, MultiArtifactDebugInput, RelatedArtifact
from .. import processing_framework
from .debug_context_builder import DebugContextBuilder
from .debug_strategy import DebugStrategyEngine
from .debug_llm_enhancer import DebugLLMEnhancer


class DebugProcessor(processing_framework.Processor):
    """
    Processes debug artifact to generate diagnosis and fixes.
    
    Features:
    - Root cause analysis for ANY error type
    - Language/framework-specific solution steps
    - Learning content generation
    - Prevention tips
    - Context enrichment (imports, configs, similar errors, docs)
    - Strategy-based diagnosis
    """
    
    stage_name = "debug_processor"
    
    def __init__(self, llm_service=None):
        super().__init__()
        self.context_builder = DebugContextBuilder()
        self.strategy_engine = DebugStrategyEngine()
        self.llm_enhancer = DebugLLMEnhancer(llm_service)
    
    def process(self, canonical_model: Union[DebugArtifact, MultiArtifactDebugInput], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process error to generate diagnosis (supports single and multi-artifact)"""
        
        # Handle both single and multi-artifact input
        if isinstance(canonical_model, MultiArtifactDebugInput):
            primary_artifact = canonical_model.primary_artifact
            related_artifacts = canonical_model.related_artifacts
        else:
            primary_artifact = canonical_model
            related_artifacts = []
        
        language = analysis.get("language", "unknown")
        framework = analysis.get("framework")
        severity = analysis.get("severity", "medium")
        error_message = analysis.get("error_message", "Unknown error")
        content = primary_artifact.content
        
        # Get strategy for this error
        strategy = self.strategy_engine.get_strategy(analysis)
        
        # Build enriched context
        context = self.context_builder.build_context(analysis, content)
        
        # Extract additional context from related artifacts
        if related_artifacts:
            context["from_multi_artifact"] = self._extract_multi_artifact_context(related_artifacts, language)
        
        # Generate root cause analysis
        root_cause = self._analyze_root_cause(content, language, framework, error_message)
        
        # Generate solution steps
        solution_steps = self._generate_solution_steps(
            language,
            framework,
            error_message,
            root_cause,
            strategy
        )
        
        # Generate learning content
        learning = self._generate_learning_content(language, root_cause, analysis, strategy)
        
        # Generate prevention tips
        prevention = self._generate_prevention_tips(root_cause, language)
        
        return {
            "summary": f"{error_message}",
            "root_cause": root_cause,
            "why_it_happened": self._explain_why(root_cause, language),
            "solution_steps": solution_steps,
            "example_code": self._generate_example(language, root_cause),
            "learning": learning,
            "prevention_tips": prevention,
            "severity": severity,
            "strategy": strategy,
            "context": context,
        }
    
    def _analyze_root_cause(self, content: str, language: str, framework: Optional[str], error_msg: str) -> str:
        """Analyze root cause - handles ANY error type"""
        
        content_lower = content.lower()
        
        # Extract error type if present (for reference)
        self._extract_error_type(content)
        
        # PYTHON ERRORS
        if language == "python":
            if "modulenotfounderror" in content_lower or "no module named" in content_lower:
                return "Module not installed or not in Python path"
            elif "importerror" in content_lower:
                return "Import path incorrect or module structure broken"
            elif "indentationerror" in content_lower or "indentation" in content_lower:
                return "Code indentation is incorrect"
            elif "indexerror" in content_lower or "list index out of range" in content_lower:
                return "List index out of bounds - accessing non-existent element"
            elif "keyerror" in content_lower:
                return "Dictionary key does not exist"
            elif "typeerror" in content_lower:
                return "Type mismatch - wrong data type used"
            elif "valueerror" in content_lower:
                return "Invalid value passed to function"
            elif "attributeerror" in content_lower:
                return "Object does not have that attribute"
            elif "nameerror" in content_lower:
                return "Variable name not defined"
            elif "zerodivisionerror" in content_lower:
                return "Division by zero"
            elif "filenotfounderror" in content_lower or "no such file" in content_lower:
                return "File does not exist at specified path"
            elif "runtimeerror" in content_lower:
                return "Runtime error during execution"
            elif "assertion" in content_lower or "assertionerror" in content_lower:
                return "Assertion failed - test condition not met"
        
        # JAVASCRIPT/NODEJS ERRORS
        if language == "javascript" or language == "typescript":
            if "cannot find module" in content_lower:
                return "Node.js module not installed"
            elif "typeerror" in content_lower and "cannot read" in content_lower:
                return "Trying to access property of null/undefined"
            elif "referenceerror" in content_lower or "is not defined" in content_lower:
                return "Variable is not defined"
            elif "syntaxerror" in content_lower:
                return "Syntax error in JavaScript code"
            elif "typeerror" in content_lower:
                return "Type error - wrong type used"
            elif "rangeerror" in content_lower:
                return "Value is outside acceptable range"
        
        # JAVA ERRORS
        if language == "java":
            if "nullpointerexception" in content_lower:
                return "Null pointer - accessing null reference"
            elif "classnotfoundexception" in content_lower:
                return "Class not found in classpath"
            elif "arrayindexoutofboundsexception" in content_lower:
                return "Array index out of bounds"
            elif "numberformatexception" in content_lower:
                return "Cannot convert string to number"
            elif "illegalargumentexception" in content_lower:
                return "Invalid argument passed to method"
        
        # SQL ERRORS
        if language == "sql":
            if "syntax error" in content_lower:
                return "SQL syntax error in query"
            elif "constraint" in content_lower and "fail" in content_lower:
                return "Database constraint violation"
            elif "table" in content_lower and ("not exist" in content_lower or "doesn't exist" in content_lower):
                return "Table does not exist in database"
            elif "column" in content_lower and ("not found" in content_lower or "doesn't exist" in content_lower):
                return "Column does not exist in table"
            elif "duplicate" in content_lower and "key" in content_lower:
                return "Duplicate key value - violates uniqueness"
            elif "foreign key" in content_lower:
                return "Foreign key constraint violated"
        
        # DOCKER/CONTAINER ERRORS
        if "docker" in content_lower or framework == "docker":
            if "no such file" in content_lower or "not found" in content_lower:
                return "Dockerfile or required file not found"
            elif "port" in content_lower and "already" in content_lower:
                return "Port already in use by another service"
            elif "image" in content_lower and "not found" in content_lower:
                return "Docker image does not exist"
        
        # KUBERNETES ERRORS
        if "kubernetes" in content_lower or "k8s" in content_lower or "pod" in content_lower:
            if "crashloopbackoff" in content_lower:
                return "Pod crashing repeatedly - check logs"
            elif "imagepullbackoff" in content_lower:
                return "Cannot pull Docker image"
            elif "pending" in content_lower:
                return "Pod stuck pending - resource/node issue"
        
        # NETWORK/CONNECTION ERRORS
        if "connection" in content_lower or "refused" in content_lower:
            return "Service not running or port unreachable"
        elif "timeout" in content_lower:
            return "Operation timed out - service unresponsive"
        elif "dns" in content_lower:
            return "DNS resolution failed"
        
        # GIT ERRORS
        if "conflict" in content_lower or "<<<<<<" in content_lower:
            return "Git merge conflict - conflicting changes"
        
        # GENERIC - Extract from error message if possible
        if error_msg and error_msg != "Unknown error":
            return f"Error: {error_msg[:100]}"
        
        return "Error occurred - check logs for details"
    
    def _extract_error_type(self, content: str) -> str:
        """Extract error type from content"""
        
        error_types = [
            "ModuleNotFoundError", "ImportError", "IndentationError", "IndexError",
            "KeyError", "TypeError", "ValueError", "AttributeError", "NameError",
            "ZeroDivisionError", "FileNotFoundError", "RuntimeError", "AssertionError",
            "NullPointerException", "ClassNotFoundException", "ArrayIndexOutOfBoundsException",
            "NumberFormatException", "IllegalArgumentException", "SyntaxError",
            "ReferenceError", "RangeError", "Exception"
        ]
        
        for err_type in error_types:
            if err_type.lower() in content.lower():
                return err_type
        
        return "Unknown"
    
    def _explain_why(self, root_cause: str, language: str) -> str:
        """Explain why this error occurred"""
        
        explanations = {
            "Module not installed or not in Python path": "You're trying to import a package that hasn't been installed or Python can't find it.",
            "Import path incorrect or module structure broken": "The module exists but the import path is wrong or the package structure is broken.",
            "Code indentation is incorrect": "Python requires consistent indentation. Tabs/spaces mismatch or wrong indent levels.",
            "List index out of bounds - accessing non-existent element": "You're trying to access a list element at an index that doesn't exist.",
            "Dictionary key does not exist": "The dictionary doesn't have the key you're trying to access.",
            "Type mismatch - wrong data type used": "You're using the wrong data type for this operation.",
            "Invalid value passed to function": "The function received a value outside its acceptable range.",
            "Object does not have that attribute": "The object doesn't have the property/method you're trying to access.",
            "Variable name not defined": "You're referencing a variable that hasn't been created or is out of scope.",
            "Division by zero": "You're trying to divide by zero, which is mathematically undefined.",
            "File does not exist at specified path": "The file you're trying to read/access doesn't exist.",
            "Node.js module not installed": "The npm package hasn't been installed in node_modules.",
            "Trying to access property of null/undefined": "The object is null or undefined, you can't access its properties.",
            "Variable is not defined": "The variable hasn't been declared or is out of scope.",
            "Null pointer - accessing null reference": "You're dereferencing a null pointer.",
            "SQL syntax error in query": "Your SQL statement has incorrect syntax for this database.",
            "Database constraint violation": "Your data violates a rule defined in the database schema.",
            "Table does not exist in database": "The table name is wrong or table hasn't been created.",
            "Column does not exist in table": "The column name is wrong or hasn't been created.",
            "Git merge conflict - conflicting changes": "Git couldn't auto-merge because both branches modified the same lines.",
            "Service not running or port unreachable": "The server/service you're trying to connect to is down or unreachable.",
            "Operation timed out - service unresponsive": "The service took too long to respond.",
        }
        
        return explanations.get(root_cause, f"The error '{root_cause}' occurred.")
    
    def _generate_solution_steps(
        self, 
        language: str, 
        framework: Optional[str], 
        error_msg: str, 
        root_cause: str,
        strategy: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate fix steps - handles any error"""
        
        steps = []
        
        # Add strategy-based checks first if available
        if strategy and "recommended_checks" in strategy:
            steps.extend(strategy["recommended_checks"][:3])
        
        # Add generic solutions
        if "not installed" in root_cause.lower() or "module" in root_cause.lower():
            if language == "python" or framework == "python":
                steps.extend([
                    "Install the package: pip install <package_name>",
                    "Check requirements.txt for all dependencies",
                    "Activate your virtual environment",
                    "Update pip: pip install --upgrade pip"
                ])
            elif language in ["javascript", "typescript"]:
                steps.extend([
                    "Install the package: npm install <package_name>",
                    "Check package.json exists",
                    "Clear node_modules: rm -rf node_modules && npm install",
                    "Check npm registry connectivity"
                ])
        
        elif "index" in root_cause.lower() or "list" in root_cause.lower():
            steps.extend([
                "Check list length before accessing by index",
                "Use len(list) to verify size",
                "Verify loop boundaries",
                "Consider using enumerate() for safe iteration"
            ])
        
        elif "key" in root_cause.lower() or "dict" in root_cause.lower():
            steps.extend([
                "Verify the dictionary key exists",
                "Use dict.get(key, default) instead of dict[key]",
                "Check key spelling and capitalization",
                "Print dictionary keys to debug"
            ])
        
        elif "type" in root_cause.lower():
            steps.extend([
                "Check variable types before operations",
                "Convert types explicitly if needed",
                "Use isinstance() to check types",
                "Add type hints for clarity"
            ])
        
        elif "null" in root_cause.lower() or "undefined" in root_cause.lower():
            steps.extend([
                "Check if object is null/undefined before using",
                "Add null checks or optional chaining",
                "Initialize variables before use",
                "Check function return values"
            ])
        
        elif "syntax" in root_cause.lower():
            steps.extend([
                "Check Python indentation (spaces vs tabs)",
                "Verify all brackets/parentheses are closed",
                "Check for missing colons or semicolons",
                "Validate code syntax with linter"
            ])
        
        elif "file" in root_cause.lower() or "path" in root_cause.lower():
            steps.extend([
                "Verify file path is correct",
                "Check if file exists at the specified location",
                "Use absolute paths if relative paths fail",
                "Check file permissions"
            ])
        
        elif "timeout" in root_cause.lower() or "connection" in root_cause.lower():
            steps.extend([
                "Verify the service is running",
                "Check network connectivity",
                "Verify correct port and hostname",
                "Increase timeout threshold if appropriate"
            ])
        
        elif "sql" in root_cause.lower():
            steps.extend([
                "Check SQL syntax against database documentation",
                "Verify all table and column names exist",
                "Test query in database client first",
                "Check data types in INSERT/UPDATE statements"
            ])
        
        elif "git" in root_cause.lower() or "conflict" in root_cause.lower():
            steps.extend([
                "Open conflicted file and review both versions",
                "Edit to keep desired changes",
                "Remove conflict markers: <<<<<<, ======, >>>>>>",
                "Stage and commit the resolved file"
            ])
        
        else:
            # Generic fallback for any error
            steps.extend([
                "Read the complete error message carefully",
                "Check the stack trace line numbers",
                "Review the code at that location",
                "Search online for similar errors",
                "Check recent code changes"
            ])
        
        return steps[:6]  # Return top 6 steps
    
    def _generate_example(self, language: str, root_cause: str) -> str:
        """Generate corrected code example"""
        
        if "index" in root_cause.lower():
            return """# WRONG:
items = ['Hat', 'Shirt', 'Jacket']
for i in range(5):  # Only 3 items!
    print(items[i])

# CORRECT:
items = ['Hat', 'Shirt', 'Jacket']
for i in range(len(items)):
    print(items[i])

# BETTER:
items = ['Hat', 'Shirt', 'Jacket']
for item in items:
    print(item)"""
        
        elif "key" in root_cause.lower():
            return """# WRONG:
data = {'name': 'John', 'age': 30}
print(data['email'])  # KeyError!

# CORRECT:
data = {'name': 'John', 'age': 30}
print(data.get('email', 'Not found'))"""
        
        elif "null" in root_cause.lower() or "undefined" in root_cause.lower():
            return """// WRONG:
let user = null;
console.log(user.name);  // TypeError!

// CORRECT:
let user = null;
if (user) {
    console.log(user.name);
}

// BETTER:
let user = null;
console.log(user?.name);  // Optional chaining"""
        
        elif "type" in root_cause.lower():
            return """# WRONG:
result = "5" + 10  # String concatenation, not addition
print(result)  # "510"

# CORRECT:
result = int("5") + 10
print(result)  # 15"""
        
        elif "import" in root_cause.lower():
            return """# WRONG:
from non_existent_module import something

# CORRECT (after pip install):
pip install requests
from requests import get"""
        
        elif "file" in root_cause.lower():
            return """# WRONG:
with open('missing.txt') as f:
    content = f.read()

# CORRECT:
import os
filepath = 'data.txt'
if os.path.exists(filepath):
    with open(filepath) as f:
        content = f.read()"""
        
        elif "syntax" in root_cause.lower():
            return """# WRONG:
if x > 5
    print("x is greater")

# CORRECT:
if x > 5:
    print("x is greater")

# Check for:
# - Missing colons after if/for/while/def
# - Mismatched parentheses/brackets
# - Invalid operators"""
        
        elif "indentation" in root_cause.lower():
            return """# WRONG:
if x > 5:
print("x is greater")  # Missing indentation!

# CORRECT:
if x > 5:
    print("x is greater")

# Rules:
# - Consistent indentation (4 spaces recommended)
# - Don't mix tabs and spaces
# - All code in a block must be at same level"""
        
        elif "attribute" in root_cause.lower():
            return """# WRONG:
user = {'name': 'John'}
print(user.name)  # Dicts don't have attributes

# CORRECT:
user = {'name': 'John'}
print(user['name'])

# OR use object:
class User:
    def __init__(self, name):
        self.name = name

user = User('John')
print(user.name)  # Now it works"""
        
        elif "name" in root_cause.lower() or "not defined" in root_cause.lower():
            return """# WRONG:
print(message)  # Variable never created

# CORRECT:
message = "Hello"
print(message)

# OR initialize before use:
if condition:
    message = "Hello"
else:
    message = "Goodbye"
print(message)"""
        
        elif "zerodivision" in root_cause.lower() or "divide by zero" in root_cause.lower():
            return """# WRONG:
result = 10 / 0  # Can't divide by zero!

# CORRECT:
divisor = 5
if divisor != 0:
    result = 10 / divisor
else:
    result = 0  # or handle error

# OR use try/except:
try:
    result = 10 / divisor
except ZeroDivisionError:
    result = 0"""
        
        elif "cannot read property" in root_cause.lower():
            return """// WRONG:
let user = null;
console.log(user.name);  // TypeError!

// CORRECT:
let user = null;
if (user && user.name) {
    console.log(user.name);
}

// OR use optional chaining:
let user = null;
console.log(user?.name);  // Returns undefined safely"""
        
        elif "nullpointer" in root_cause.lower():
            return """// WRONG:
String name = null;
int length = name.length();  // NullPointerException!

// CORRECT:
String name = null;
if (name != null) {
    int length = name.length();
}

// OR use Objects.requireNonNull:
String name = Objects.requireNonNull(name);
int length = name.length();"""
        
        elif "sql" in root_cause.lower():
            return """-- WRONG:
SELECT * FROM users WHERE age = 25
SELECT * FROM products

-- CORRECT (proper syntax and termination):
SELECT * FROM users WHERE age = 25;
SELECT * FROM products;

-- Common mistakes:
-- 1. Missing WHERE clause (returns all rows)
-- 2. Typos in column/table names
-- 3. Missing quotes around string values
-- 4. Incorrect operator (= vs ==)"""
        
        elif "conflict" in root_cause.lower() or "merge" in root_cause.lower():
            return """# WRONG (File with conflict markers):
<<<<<<< HEAD
print("Version A")
=======
print("Version B")
>>>>>>> branch-name

# CORRECT (Pick one version and remove markers):
print("Version A")  # or "Version B" if preferred

# Steps:
# 1. Open the conflicted file
# 2. Review both versions
# 3. Keep desired code
# 4. Delete <<<<<<, ======, >>>>>>
# 5. git add file
# 6. git commit -m 'Resolved merge conflict'"""        
        else:
            return "# Review the error message above for specific details"
    
    def _generate_learning_content(
        self, 
        language: str, 
        root_cause: str,
        analysis: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enriched learning content with strategy integration"""
        
        category = analysis.get("category", "unknown")
        
        # Build concept explanations by category
        concepts = {
            "import_error": "How module resolution and package management works",
            "type_error": "Type systems, type checking, and type conversion",
            "syntax_error": "Language grammar, syntax rules, and code structure",
            "runtime_error": "Runtime execution flow and error handling",
            "database_error": "Database design, constraints, and query execution",
            "network_error": "Network protocols, connections, and timeouts",
            "validation_error": "Data validation, schema checking, and constraints",
            "authentication_error": "Authentication, authorization, and permissions",
            "merge_conflict": "Version control, branching, and merge strategies",
            "configuration_error": "Configuration management and environment setup",
        }
        
        concept = concepts.get(category, "Error handling and debugging")
        
        # Extract common mistakes from strategy
        common_mistakes = []
        if strategy and "likely_causes" in strategy:
            common_mistakes = strategy["likely_causes"][:4]
        
        # Extract prevention strategies from strategy
        prevention = []
        if strategy and "recommended_checks" in strategy:
            prevention = strategy["recommended_checks"][:4]
        
        # Extract best practices from strategy
        best_practices = []
        if strategy and "focus_areas" in strategy:
            best_practices = strategy["focus_areas"][:3]
        
        # Create mental model
        mental_model = self._create_mental_model(category, root_cause, language)
        
        return {
            "concept_explained": concept,
            "understanding": self._explain_why(root_cause, language),
            "when_it_happens": f"This occurs in {language} when {root_cause.lower()}",
            "common_mistakes": common_mistakes,
            "prevention_strategies": prevention,
            "best_practices": best_practices,
            "mental_model": mental_model,
            "documentation_sections": strategy.get("documentation_sections", []) if strategy else [],
        }
    
    def _create_mental_model(self, category: str, root_cause: str, language: str) -> str:
        """Create a mental model explanation for the error"""
        
        models = {
            "import_error": "Think of imports like borrowing a book from a library. Python must find the book (module) and bring it into your workspace. If it's not there or the path is wrong, you can't use it.",
            "type_error": "Types are like containers. You can't put a string into a math operation that expects a number. Type mismatches happen when containers don't match what the operation needs.",
            "syntax_error": "Syntax is like grammar in English. Missing colons or parentheses are like missing punctuation - the computer can't understand incomplete sentences.",
            "runtime_error": "Runtime errors happen during execution. It's like following a recipe - you can follow all the steps correctly, but if you use the wrong ingredient, it fails when you try to cook.",
            "database_error": "Think of a database like a filing system. Each table is a drawer, each column is a folder, and each row is a file. You must reference files that exist and follow the filing rules.",
            "network_error": "Networks are like phone calls. If the phone is off (service down), the line is busy (timeout), or the number is wrong (port), the call fails.",
            "validation_error": "Validation is like a bouncer at a club checking ID. Data must meet the requirements (age check) to be accepted.",
            "authentication_error": "Authentication is proving you are who you say you are (ID check). Authorization is having permission to do something (VIP access).",
            "merge_conflict": "Git conflicts happen when two people edit the same lines differently. Git can't decide which version to keep, so it asks you.",
        }
        
        return models.get(category, "Review the error context and documentation for details")
    
    def _generate_prevention_tips(self, root_cause: str, language: str) -> List[str]:
        """Generate tips to prevent this error"""
        
        tips = [
            "Read error messages carefully - they tell you exactly what's wrong",
            "Use proper error handling (try/except, try/catch)",
            "Test your code with various inputs",
            "Use linting and type checking tools",
        ]
        
        if "index" in root_cause.lower() or "list" in root_cause.lower():
            tips.extend([
                "Always verify list length before accessing by index",
                "Use len() function to check boundaries",
                "Prefer iteration over manual indexing",
            ])
        
        if "key" in root_cause.lower() or "dict" in root_cause.lower():
            tips.extend([
                "Use .get() method instead of direct key access",
                "Document expected dictionary keys",
                "Validate dictionary structure at boundaries",
            ])
        
        if "module" in root_cause.lower() or "import" in root_cause.lower():
            tips.extend([
                "Keep requirements.txt updated",
                "Use virtual environments",
                "Test imports before deployment",
            ])
        
        if "null" in root_cause.lower() or "undefined" in root_cause.lower():
            tips.extend([
                "Initialize variables before use",
                "Check for null/undefined before accessing properties",
                "Use optional chaining when available",
            ])
        
        if "type" in root_cause.lower():
            tips.extend([
                "Be explicit about type conversions",
                "Use type hints in function signatures",
                "Check types before operations",
            ])
        
        return tips
    
    def _extract_multi_artifact_context(self, related_artifacts: List[RelatedArtifact], language: str) -> Dict[str, Any]:
        """Extract additional context from related artifacts"""
        
        context = {
            "has_code": False,
            "has_config": False,
            "has_requirements": False,
            "code_languages": [],
            "config_files": [],
        }
        
        for artifact in related_artifacts:
            if artifact.artifact_type == "code":
                context["has_code"] = True
                if artifact.language:
                    context["code_languages"].append(artifact.language)
            elif artifact.artifact_type == "config" or artifact.artifact_type == "requirements":
                context["has_config"] = True
                context["has_requirements"] = artifact.artifact_type == "requirements"
                if artifact.filename:
                    context["config_files"].append(artifact.filename)
        
        return context

    def enhance_with_llm(self, processing_result: Dict[str, Any], analysis: Dict[str, Any], error_artifact: Optional[str] = None) -> Dict[str, Any]:
        """
        Optionally enhance debug analysis with LLM reasoning
        
        Args:
            processing_result: Result from process() method  
            analysis: Analysis metadata dict from analyzer
            error_artifact: Original error text/artifact
        
        Returns:
            Enhanced processing result with LLM insights
        """
        
        if not self.llm_enhancer.llm_service:
            return processing_result
        
        try:
            from .debug_models import AnalysisMetadata, DebugStrategy
            
            # Convert analysis dict to AnalysisMetadata object
            metadata = AnalysisMetadata(**analysis)
            
            # Get strategy (returns dict)
            strategy_dict = self.strategy_engine.get_strategy(analysis)
            
            # Convert strategy dict to DebugStrategy object
            strategy = DebugStrategy(
                strategy_type=strategy_dict.get("strategy_type", "general"),
                focus_areas=strategy_dict.get("focus_areas", []),
                recommended_checks=strategy_dict.get("recommended_checks", []),
                likely_causes=strategy_dict.get("likely_causes", []),
                documentation_sections=strategy_dict.get("documentation_sections", []),
            )
            
            # Use the provided artifact or fall back to summary
            error_content = error_artifact or processing_result.get("summary", "")
            
            # Enhance with LLM - only root cause for speed
            print(f"[LLM] Enhancing with {self.llm_enhancer.llm_service.default_provider}...")
            enhanced_root_cause = self.llm_enhancer.enhance_root_cause(
                metadata, strategy, error_content
            )
            print("[LLM] Root cause enhancement complete")
            
            # Merge enhancements
            processing_result["root_cause"] = enhanced_root_cause.root_cause
            processing_result["why_it_happened"] = enhanced_root_cause.why_it_happened
            processing_result["llm_enhanced"] = True
            
            return processing_result
        
        except Exception as e:
            print(f"LLM enhancement error in processor: {e}")
            processing_result["llm_enhanced"] = False
            return processing_result
