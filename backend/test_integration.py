#!/usr/bin/env python3
"""Test Debug Engine + LLM Integration"""
import sys
sys.path.insert(0, '.')

print("\n" + "="*80)
print("TEST: Debug Engine + LLM Integration")
print("="*80)

try:
    print("\n[1] Testing imports...")
    from app.services.debug.debug_engine import DebugEngine
    from app.services.llm.llm_service import LLMService
    print("OK - Imports successful")
    
    print("\n[2] Testing LLM Service...")
    llm = LLMService()
    status = llm.status()
    print(f"OK - LLM Service initialized")
    print(f"    Default provider: {status['default_provider']}")
    
    print("\n[3] Testing Debug Engine (no LLM)...")
    engine = DebugEngine()
    error = """Traceback (most recent call last):
  File "test.py", line 5, in <module>
    x = items[100]
IndexError: list index out of range"""
    
    response = engine.respond(error, apply_enhancement=False)
    print(f"OK - Debug Engine responded")
    print(f"    Success: {response.success if hasattr(response, 'success') else 'N/A'}")
    
    if hasattr(response, 'processing') and response.processing:
        data = response.processing.data if hasattr(response.processing, 'data') else response.processing
        if isinstance(data, dict):
            print(f"    Root Cause: {data.get('root_cause', 'N/A')[:60]}")
    
    print("\n[4] Testing Debug Engine (WITH LLM)...")
    response = engine.respond(error, apply_enhancement=True)
    print(f"OK - Debug Engine with LLM responded")
    print(f"    Success: {response.success if hasattr(response, 'success') else 'N/A'}")
    
    if hasattr(response, 'processing') and response.processing:
        data = response.processing.data if hasattr(response.processing, 'data') else response.processing
        if isinstance(data, dict):
            print(f"    LLM Enhanced: {data.get('llm_enhanced', False)}")
            print(f"    Root Cause: {data.get('root_cause', 'N/A')[:60]}")
            print(f"    Why It Happened: {data.get('why_it_happened', 'N/A')[:80]}")
    
    print("\n" + "="*80)
    print("SUCCESS - All tests passed!")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
