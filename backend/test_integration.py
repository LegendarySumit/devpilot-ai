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
    
    print("\n[3] Testing Debug Engine (IndexError - Known Handler)...")
    engine = DebugEngine()
    error = """Traceback (most recent call last):
  File "test.py", line 5, in <module>
    x = items[100]
IndexError: list index out of range"""
    
    response = engine.respond(error, apply_enhancement=False)
    print(f"OK - Debug Engine responded")
    if response.processing:
        data = response.processing.data if hasattr(response.processing, 'data') else response.processing
        print(f"    Root Cause: {data.get('root_cause', 'N/A')[:60]}...")
        print(f"    Confidence: {data.get('confidence', 0):.0%}")
    
    print("\n[4] Testing Debug Engine (NameError - Known Handler)...")
    error = """Traceback (most recent call last):
  File "main.py", line 7, in get_user
    return {"id": user_id}
NameError: name 'user_id' is not defined"""
    
    response = engine.respond(error, apply_enhancement=False)
    print(f"OK - Debug Engine responded")
    if response.processing:
        data = response.processing.data if hasattr(response.processing, 'data') else response.processing
        print(f"    Root Cause: {data.get('root_cause', 'N/A')}")
        print(f"    Confidence: {data.get('confidence', 0):.0%}")
    
    print("\n[5] Testing Debug Engine (SQLAlchemy - UNKNOWN, uses LLM)...")
    error = """sqlalchemy.exc.IntegrityError:
(psycopg2.errors.UniqueViolation)
duplicate key value violates unique constraint "users_email_key"

DETAIL:
Key (email)=(john@example.com) already exists."""
    
    response = engine.respond(error, apply_enhancement=True)
    print(f"OK - Debug Engine with LLM responded")
    if response.processing:
        data = response.processing.data if hasattr(response.processing, 'data') else response.processing
        print(f"    Root Cause: {data.get('root_cause', 'N/A')[:80]}...")
        print(f"    Confidence: {data.get('confidence', 0):.0%}")
        print(f"    LLM Enhanced: {data.get('llm_enhanced', False)}")
    
    print("\n" + "="*80)
    print("SUCCESS - All tests passed!")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
