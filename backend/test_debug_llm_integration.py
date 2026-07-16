"""
Complete Debug Engine + LLM Integration Test
Tests real errors with both rule-based and LLM-enhanced responses
"""

from app.services.debug.debug_engine import DebugEngine
import json

def print_response(title, response, show_llm=False):
    """Pretty print response"""
    print(f"\n{'='*70}")
    print(f"TEST: {title}")
    print(f"{'='*70}")
    
    if hasattr(response, 'success'):
        print(f"✅ Success: {response.success}")
    
    if hasattr(response, 'confidence_score'):
        print(f"📊 Confidence: {response.confidence_score}")
    
    if hasattr(response, 'processing') and response.processing:
        data = response.processing.data if hasattr(response.processing, 'data') else response.processing
        
        if isinstance(data, dict):
            print(f"\n📋 ROOT CAUSE:")
            print(f"   {data.get('root_cause', 'N/A')}")
            
            print(f"\n❓ WHY IT HAPPENED:")
            print(f"   {data.get('why_it_happened', 'N/A')}")
            
            print(f"\n🔧 SOLUTION STEPS:")
            steps = data.get('solution_steps', [])
            if isinstance(steps, list):
                for i, step in enumerate(steps, 1):
                    print(f"   {i}. {step}")
            
            if show_llm:
                llm_enhanced = data.get('llm_enhanced', False)
                print(f"\n🤖 LLM Enhanced: {llm_enhanced}")
            
            print(f"\n💡 LEARNING:")
            learning = data.get('learning', {})
            if isinstance(learning, dict):
                print(f"   Concept: {learning.get('concept_explained', 'N/A')}")
                print(f"   Prevention: {learning.get('prevention_strategies', [])[:2]}")


def test_python_index_error():
    """Test Python IndexError"""
    print("\n\n" + "█"*70)
    print("TEST 1: Python IndexError (Rule-Based)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """Traceback (most recent call last):
  File "script.py", line 6, in <module>
    print(items[i])
IndexError: list index out of range"""
    
    response = engine.respond(error, apply_enhancement=False)
    print_response("Python IndexError", response)
    
    return response.success if hasattr(response, 'success') else False


def test_python_index_error_with_llm():
    """Test Python IndexError WITH LLM enhancement"""
    print("\n\n" + "█"*70)
    print("TEST 2: Python IndexError (WITH LLM Enhancement)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """Traceback (most recent call last):
  File "script.py", line 6, in <module>
    print(items[i])
IndexError: list index out of range"""
    
    response = engine.respond(error, apply_enhancement=True)
    print_response("Python IndexError + LLM", response, show_llm=True)
    
    return response.success if hasattr(response, 'success') else False


def test_module_not_found_error():
    """Test ModuleNotFoundError"""
    print("\n\n" + "█"*70)
    print("TEST 3: ModuleNotFoundError (Rule-Based)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """Traceback (most recent call last):
  File "app.py", line 2, in <module>
    import fastapi
ModuleNotFoundError: No module named 'fastapi'"""
    
    response = engine.respond(error, apply_enhancement=False)
    print_response("ModuleNotFoundError", response)
    
    return response.success if hasattr(response, 'success') else False


def test_module_not_found_with_llm():
    """Test ModuleNotFoundError WITH LLM"""
    print("\n\n" + "█"*70)
    print("TEST 4: ModuleNotFoundError (WITH LLM Enhancement)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """Traceback (most recent call last):
  File "app.py", line 2, in <module>
    import fastapi
ModuleNotFoundError: No module named 'fastapi'"""
    
    response = engine.respond(error, apply_enhancement=True)
    print_response("ModuleNotFoundError + LLM", response, show_llm=True)
    
    return response.success if hasattr(response, 'success') else False


def test_syntax_error():
    """Test SyntaxError"""
    print("\n\n" + "█"*70)
    print("TEST 5: SyntaxError (Rule-Based)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """File "main.py", line 15
    if x == 5
           ^
SyntaxError: invalid syntax"""
    
    response = engine.respond(error, apply_enhancement=False)
    print_response("SyntaxError", response)
    
    return response.success if hasattr(response, 'success') else False


def test_type_error():
    """Test TypeError"""
    print("\n\n" + "█"*70)
    print("TEST 6: TypeError (Rule-Based)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """Traceback (most recent call last):
  File "calc.py", line 10, in <module>
    result = len(42)
TypeError: object of type 'int' has no len()"""
    
    response = engine.respond(error, apply_enhancement=False)
    print_response("TypeError", response)
    
    return response.success if hasattr(response, 'success') else False


def test_javascript_error():
    """Test JavaScript ReferenceError"""
    print("\n\n" + "█"*70)
    print("TEST 7: JavaScript ReferenceError (Rule-Based)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """ReferenceError: Cannot find variable myVar
at app.js:25:15"""
    
    response = engine.respond(error, apply_enhancement=False)
    print_response("JavaScript ReferenceError", response)
    
    return response.success if hasattr(response, 'success') else False


def test_sql_error():
    """Test SQL Syntax Error"""
    print("\n\n" + "█"*70)
    print("TEST 8: SQL Syntax Error (Rule-Based)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """SQL Error: 
SELECT * FROM users WHRE id = 1
                     ^
Syntax error near 'WHRE'"""
    
    response = engine.respond(error, apply_enhancement=False)
    print_response("SQL Syntax Error", response)
    
    return response.success if hasattr(response, 'success') else False


def test_docker_error():
    """Test Docker error"""
    print("\n\n" + "█"*70)
    print("TEST 9: Docker Build Error (Rule-Based)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """Step 5/10 : RUN pip install -r requirements.txt
 ---> Running in abc123def456
ERROR: Could not find a version that satisfies the requirement numpy==999.0.0"""
    
    response = engine.respond(error, apply_enhancement=False)
    print_response("Docker Error", response)
    
    return response.success if hasattr(response, 'success') else False


def test_git_merge_conflict():
    """Test Git merge conflict"""
    print("\n\n" + "█"*70)
    print("TEST 10: Git Merge Conflict (Rule-Based)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """CONFLICT (content): Merge conflict in main.py
Auto-merging main.py
CONFLICT (add/add): Merge conflict in config.json
Automatic merge failed; fix conflicts and then commit the result."""
    
    response = engine.respond(error, apply_enhancement=False)
    print_response("Git Merge Conflict", response)
    
    return response.success if hasattr(response, 'success') else False


def test_learning_mode():
    """Test with learning mode enabled"""
    print("\n\n" + "█"*70)
    print("TEST 11: Learning Mode (Educational Content)")
    print("█"*70)
    
    engine = DebugEngine()
    
    error = """Traceback (most recent call last):
  File "script.py", line 5, in <module>
    x = None
    y = x + 5
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'"""
    
    response = engine.respond(error, apply_enhancement=False, learning_mode=True)
    print_response("TypeError with Learning Mode", response)
    
    return response.success if hasattr(response, 'success') else False


def test_multi_artifact():
    """Test multi-artifact debugging"""
    print("\n\n" + "█"*70)
    print("TEST 12: Multi-Artifact Debugging (Error + Code + Config)")
    print("█"*70)
    
    engine = DebugEngine()
    
    multi_artifact = {
        "primary_artifact": {
            "content": "ModuleNotFoundError: No module named 'flask'",
            "artifact_type": "error"
        },
        "related_artifacts": [
            {
                "artifact_type": "code",
                "content": "import flask\napp = flask.Flask(__name__)"
            },
            {
                "artifact_type": "config",
                "content": "requirements.txt:\n numpy==1.21.0\n pandas==1.3.0"
            }
        ]
    }
    
    response = engine.respond(multi_artifact, apply_enhancement=False)
    print_response("Multi-Artifact Debug", response)
    
    return response.success if hasattr(response, 'success') else False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 DEBUG ENGINE + LLM INTEGRATION TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Rule-based tests (should always work)
    results["Python IndexError (Rule)"] = test_python_index_error()
    results["ModuleNotFoundError (Rule)"] = test_module_not_found_error()
    results["SyntaxError (Rule)"] = test_syntax_error()
    results["TypeError (Rule)"] = test_type_error()
    results["JavaScript Error (Rule)"] = test_javascript_error()
    results["SQL Error (Rule)"] = test_sql_error()
    results["Docker Error (Rule)"] = test_docker_error()
    results["Git Conflict (Rule)"] = test_git_merge_conflict()
    results["Learning Mode"] = test_learning_mode()
    results["Multi-Artifact"] = test_multi_artifact()
    
    # LLM-enhanced tests (should work if LLM available)
    results["Python IndexError + LLM"] = test_python_index_error_with_llm()
    results["ModuleNotFoundError + LLM"] = test_module_not_found_with_llm()
    
    # Print summary
    print("\n\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
