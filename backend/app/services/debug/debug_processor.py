"""
Debug Processor - Intelligent error analysis WITHOUT relying on LLM
Only uses LLM when confidence is low or for educational content
"""
import re
from typing import Dict, Any, Optional, Union
from .debug_models import DebugArtifact, MultiArtifactDebugInput
from .. import processing_framework


class DebugProcessor(processing_framework.Processor):
    """
    Intelligent error analysis before LLM
    
    Strategy:
    1. Extract error details from traceback
    2. Apply intelligent pattern detection
    3. Generate high-confidence diagnosis
    4. Only call LLM for low-confidence cases
    """
    
    stage_name = "debug_processor"
    
    def __init__(self, llm_service=None):
        super().__init__()
        self.llm_service = llm_service
        # Lazy load LLM enhancer
        self._llm_enhancer = None
    
    def process(self, canonical_model: Union[DebugArtifact, MultiArtifactDebugInput], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligent error analysis"""
        
        if isinstance(canonical_model, MultiArtifactDebugInput):
            error_content = canonical_model.primary_artifact.content
        else:
            error_content = canonical_model.content
        
        language = analysis.get("language", "unknown")
        category = analysis.get("category", "unknown")
        
        # Step 1: Extract error details
        error_details = self._extract_error_details(error_content, language)
        
        # Step 2: Intelligent analysis based on error type
        diagnosis = self._analyze_intelligent(error_details, language, category, error_content)
        
        return {
            "summary": error_details.get("error_message", "Unknown error"),
            "root_cause": diagnosis["root_cause"],
            "why_it_happened": diagnosis["why_it_happened"],
            "solution_steps": diagnosis["solution_steps"],
            "confidence": diagnosis["confidence"],
            "need_llm": diagnosis["confidence"] < 0.7,  # Only use LLM if unsure
            "error_details": error_details,
        }
    
    # ========================================================================
    # STEP 1: EXTRACT ERROR DETAILS FROM TRACEBACK
    # ========================================================================
    
    def _extract_error_details(self, error_content: str, language: str) -> Dict[str, Any]:
        """Extract file, line, function, variable info from error"""
        
        details: Dict[str, Any] = {
            "file": None,
            "line_number": None,
            "function": None,
            "error_type": None,
            "error_message": None,
            "variable_name": None,
            "import_name": None,
            "attribute_name": None,
            "index_value": None,
        }
        
        if language == "python":
            # Extract file and line: File "main.py", line 7
            file_match = re.search(r'File "([^"]+)", line (\d+)', error_content)
            if file_match:
                details["file"] = file_match.group(1)
                details["line_number"] = int(file_match.group(2))
            
            # Extract function: in function_name
            func_match = re.search(r'in ([a-zA-Z_]\w*)', error_content)
            if func_match:
                details["function"] = func_match.group(1)
            
            # Extract error type and message
            error_type_match = re.search(r'(\w+Error):\s*(.+)$', error_content, re.MULTILINE)
            if error_type_match:
                details["error_type"] = error_type_match.group(1)
                details["error_message"] = error_type_match.group(2).strip()
            
            # Extract variable name from NameError
            if "NameError" in error_content:
                var_match = re.search(r"name '([^']+)' is not defined", error_content)
                if var_match:
                    details["variable_name"] = var_match.group(1)
            
            # Extract import name from ImportError
            if "ImportError" in error_content or "ModuleNotFoundError" in error_content:
                import_match = re.search(r"cannot import name '([^']+)'|No module named '([^']+)'", error_content)
                if import_match:
                    details["import_name"] = import_match.group(1) or import_match.group(2)
            
            # Extract attribute from AttributeError
            if "AttributeError" in error_content:
                attr_match = re.search(r"has no attribute '([^']+)'", error_content)
                if attr_match:
                    details["attribute_name"] = attr_match.group(1)
            
            # Extract index from IndexError
            if "IndexError" in error_content:
                idx_match = re.search(r"\[(\d+)\]", error_content)
                if idx_match:
                    details["index_value"] = int(idx_match.group(1))
        else:
            # For non-Python errors (SQL, etc), extract first line with error as message
            first_line = error_content.split('\n')[0].strip()
            if first_line:
                details["error_message"] = first_line
                # Try to extract error type from exception format
                if "." in first_line:
                    details["error_type"] = first_line.split(":")[0].split(".")[-1].strip()
        
        # Fallback: if no error_message found, use first meaningful line
        if not details["error_message"]:
            for line in error_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    details["error_message"] = line
        
        return details
    
    # ========================================================================
    # STEP 2: INTELLIGENT PATTERN-BASED ANALYSIS
    # ========================================================================
    
    def _analyze_intelligent(self, details: Dict[str, Any], language: str, category: str, error_content: str) -> Dict[str, Any]:
        """Apply intelligent pattern detection for specific error types"""
        
        error_type = details.get("error_type", "")
        var_name = details.get("variable_name")
        import_name = details.get("import_name")
        attr_name = details.get("attribute_name")
        index_val = details.get("index_value")
        
        # PYTHON ERRORS
        if language == "python":
            # 1. NameError: variable not defined
            if error_type == "NameError" and var_name:
                return self._analyze_nameerror(var_name, details, error_content)
            
            # 2. ImportError: cannot import name
            elif error_type == "ImportError" and import_name:
                return self._analyze_importerror_name(import_name, error_content)
            
            # 3. ModuleNotFoundError
            elif error_type == "ModuleNotFoundError" and import_name:
                return self._analyze_modulenotfound(import_name)
            
            # 4. AttributeError
            elif error_type == "AttributeError" and attr_name:
                return self._analyze_attributeerror(attr_name, details, error_content)
            
            # 5. IndexError
            elif error_type == "IndexError" and index_val is not None:
                return self._analyze_indexerror(index_val, details)
            
            # 6. TypeError
            elif error_type == "TypeError":
                return self._analyze_typeerror(details, error_content)
            
            # 7. SyntaxError
            elif error_type == "SyntaxError":
                return self._analyze_syntaxerror(details, error_content)
            
            # 8. KeyError
            elif error_type == "KeyError":
                return self._analyze_keyerror(details, error_content)
        
        # Default: generic analysis
        return self._analyze_generic(details, error_content)
    
    # ========================================================================
    # SPECIFIC ERROR ANALYZERS
    # ========================================================================
    
    def _analyze_nameerror(self, var_name: str, details: Dict[str, Any], error_content: str) -> Dict[str, Any]:
        """Analyze NameError: name 'X' is not defined"""
        
        return {
            "root_cause": f"Variable '{var_name}' is not defined in the current scope",
            "why_it_happened": f"The variable '{var_name}' is being used in {details.get('function', 'the code')} "
                             f"(line {details.get('line_number', '?')}), but it was never created, assigned, or passed as a parameter. "
                             f"Python scoping rules mean it must be defined before use.",
            "solution_steps": [
                f"Option 1: Add '{var_name}' as a parameter to {details.get('function', 'your function')}()",
                f"Option 2: Define '{var_name}' before using it in the function",
                f"Option 3: Make '{var_name}' a global variable if needed",
                f"Option 4: Check if '{var_name}' is imported from another module",
            ],
            "confidence": 0.95,  # Very high confidence for NameError
        }
    
    def _analyze_importerror_name(self, import_name: str, error_content: str) -> Dict[str, Any]:
        """Analyze ImportError: cannot import name 'X' from 'Y'"""
        
        # Check if it's a pydantic BaseSettings issue (common in v2)
        if import_name == "BaseSettings" and "pydantic" in error_content:
            return {
                "root_cause": f"'{import_name}' was moved from 'pydantic' to 'pydantic_settings' in Pydantic v2",
                "why_it_happened": f"Pydantic v2 restructured the library. '{import_name}' is no longer in the main pydantic module. "
                                 f"It was moved to the pydantic_settings submodule to separate core functionality from settings management.",
                "solution_steps": [
                    "Change: from pydantic import BaseSettings",
                    "To: from pydantic_settings import BaseSettings",
                    "Install if needed: pip install pydantic-settings",
                    "Update all imports in your codebase",
                ],
                "confidence": 0.98,  # Very specific fix
            }
        
        # Generic import error
        return {
            "root_cause": f"'{import_name}' cannot be imported from the specified module",
            "why_it_happened": f"Either: (1) '{import_name}' doesn't exist in that module, "
                             f"(2) It was removed/renamed in a newer version, or (3) The module structure changed.",
            "solution_steps": [
                "Check the module documentation for correct import path",
                f"Verify '{import_name}' exists in the module",
                "Check if it was renamed or moved in newer versions",
                "Update the import statement accordingly",
            ],
            "confidence": 0.70,
        }
    
    def _analyze_modulenotfound(self, module_name: str) -> Dict[str, Any]:
        """Analyze ModuleNotFoundError: No module named 'X'"""
        
        return {
            "root_cause": f"Module '{module_name}' is not installed in your Python environment",
            "why_it_happened": f"The code is trying to import '{module_name}', but it's not installed. "
                             f"Python can only import packages that are installed in the current environment or in the system path.",
            "solution_steps": [
                f"Install the module: pip install {module_name.split('.')[0]}",
                f"Verify installation: pip list | grep {module_name.split('.')[0]}",
                "Ensure you're using the correct virtual environment",
                "Check requirements.txt or setup.py for correct module name",
            ],
            "confidence": 0.96,
        }
    
    def _analyze_attributeerror(self, attr_name: str, details: Dict[str, Any], error_content: str) -> Dict[str, Any]:
        """Analyze AttributeError: object has no attribute 'X'"""
        
        return {
            "root_cause": f"Object doesn't have attribute '{attr_name}'",
            "why_it_happened": f"You're trying to access '{attr_name}' on an object that doesn't have it. "
                             "Either: (1) The object type is wrong, (2) The attribute was renamed, "
                             f"(3) The attribute only exists after initialization, or (4) Wrong object instance.",
            "solution_steps": [
                "Check the object type - print(type(object))",
                f"Verify '{attr_name}' exists in that class/object",
                "Check if initialization is complete before accessing",
                "Review the class definition or documentation",
                "Check if the attribute was renamed in newer versions",
            ],
            "confidence": 0.75,
        }
    
    def _analyze_indexerror(self, index_val: int, details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze IndexError: list index out of range"""
        
        return {
            "root_cause": f"List/sequence index {index_val} is out of bounds - the sequence is too small",
            "why_it_happened": f"You're trying to access index {index_val}, but the list/sequence doesn't have that many elements. "
                             f"Arrays are 0-indexed, so a list with 3 elements has valid indices 0, 1, 2 (not 3).",
            "solution_steps": [
                "Check the size of the list: print(len(my_list))",
                f"Verify index {index_val} is valid (must be < length)",
                f"Add bounds checking: if {index_val} < len(my_list):",
                "Use negative indexing if trying to access from end: my_list[-1]",
                "Check loop conditions don't exceed list length",
            ],
            "confidence": 0.94,
        }
    
    def _analyze_typeerror(self, details: Dict[str, Any], error_content: str) -> Dict[str, Any]:
        """Analyze TypeError: unsupported operand type(s)"""
        
        if "unsupported operand" in error_content:
            # Extract types involved
            type_match = re.search(r"'([^']+)' and '([^']+)'", error_content)
            if type_match:
                type1, type2 = type_match.group(1), type_match.group(2)
                return {
                    "root_cause": f"Cannot use operator on {type1} and {type2} types",
                    "why_it_happened": "You're trying to use an operation (like +, -, *, /) on incompatible types. "
                                     "For example: can't add string + number without conversion.",
                    "solution_steps": [
                        "Convert types to match: str(value), int(value), float(value)",
                        "Use str.format() or f-strings for string concatenation",
                        "Check variable types with type(variable)",
                        "Review the operation - is it valid for these types?",
                    ],
                    "confidence": 0.85,
                }
        
        return {
            "root_cause": "Type mismatch in operation",
            "why_it_happened": "You're performing an operation on incompatible data types.",
            "solution_steps": [
                "Check the types of both operands",
                "Convert to compatible types",
                "Use type checking before operations",
            ],
            "confidence": 0.65,
        }
    
    def _analyze_syntaxerror(self, details: Dict[str, Any], error_content: str) -> Dict[str, Any]:
        """Analyze SyntaxError"""
        
        common_issues = []
        if ":" in error_content:
            common_issues.append("Missing colon (:) after if/for/while/def")
        if "(" in error_content or ")" in error_content:
            common_issues.append("Mismatched parentheses/brackets")
        if "=" in error_content:
            common_issues.append("Assignment in wrong place (use == for comparison)")
        
        return {
            "root_cause": "Python syntax error in code",
            "why_it_happened": f"Line {details.get('line_number', '?')} has invalid Python syntax. Common issues: missing colons, mismatched brackets, wrong indentation.",
            "solution_steps": [
                f"Check line {details.get('line_number', '?')} for syntax mistakes",
                "Verify all colons after if/for/while/def/class",
                "Check matching parentheses/brackets/braces",
                "Fix indentation (Python is whitespace-sensitive)",
                "Use a Python linter (pylint, flake8) to catch errors",
            ],
            "confidence": 0.80,
        }
    
    def _analyze_keyerror(self, details: Dict[str, Any], error_content: str) -> Dict[str, Any]:
        """Analyze KeyError"""
        
        key_match = re.search(r"'([^']+)'", error_content)
        key_name = key_match.group(1) if key_match else "key"
        
        return {
            "root_cause": f"Dictionary key '{key_name}' does not exist",
            "why_it_happened": f"You're trying to access dict['{key_name}'], but that key wasn't added to the dictionary. Dictionaries only have keys that were explicitly set.",
            "solution_steps": [
                f'Check if "{key_name}" is in the dict: if "{key_name}" in my_dict:',
                f'Use .get() method: my_dict.get("{key_name}", default_value)',
                "Print all keys: print(my_dict.keys())",
                f'Add the key if missing: my_dict["{key_name}"] = value',
            ],
            "confidence": 0.92,
        }
    
    def _analyze_generic(self, details: Dict[str, Any], error_content: str) -> Dict[str, Any]:
        """Fallback for unknown errors"""
        
        return {
            "root_cause": f"{details.get('error_type', 'Unknown')} error occurred",
            "why_it_happened": "An error was raised but couldn't be specifically analyzed. Review the error message and traceback carefully.",
            "solution_steps": [
                "Read the error message thoroughly",
                "Check the exact line number in traceback",
                "Search documentation for the error type",
                "Review recent code changes",
            ],
            "confidence": 0.50,  # Low confidence - needs LLM
        }
    
    # ========================================================================
    # LLM ENHANCEMENT (Only for low confidence or learning)
    # ========================================================================
    
    def enhance_with_llm(self, processing_result: Dict[str, Any], analysis: Dict[str, Any], error_artifact: Optional[str] = None) -> Dict[str, Any]:
        """Call LLM only for clarification or learning content"""
        
        if not self.llm_service:
            return processing_result
        
        try:
            # Lazy load LLM enhancer
            if not self._llm_enhancer:
                from .debug_llm_enhancer import DebugLLMEnhancer
                self._llm_enhancer = DebugLLMEnhancer(self.llm_service)
            
            from .debug_models import AnalysisMetadata, DebugStrategy
            
            metadata = AnalysisMetadata(**analysis)
            strategy = DebugStrategy(
                strategy_type="enhance",
                focus_areas=[],
                recommended_checks=[],
                likely_causes=[],
                documentation_sections=[],
            )
            
            error_content = error_artifact or processing_result.get("summary", "")
            confidence = processing_result.get("confidence", 1.0)
            
            # Get LLM-based analysis
            enhanced = self._llm_enhancer.enhance_root_cause(
                metadata, strategy, error_content
            )
            
            processing_result["root_cause"] = enhanced.root_cause
            processing_result["why_it_happened"] = enhanced.why_it_happened
            
            # If confidence is very low, also generate solution steps
            if confidence < 0.6:
                try:
                    solution = self._llm_enhancer.enhance_solution(
                        metadata, strategy, error_content
                    )
                    if solution and hasattr(solution, 'steps'):
                        processing_result["solution_steps"] = solution.steps
                except Exception as e:
                    print(f"Failed to generate solution steps: {e}")
            
            processing_result["llm_enhanced"] = True
            
            return processing_result
        
        except Exception as e:
            print(f"LLM enhancement error: {e}")
            processing_result["llm_enhanced"] = False
            return processing_result
