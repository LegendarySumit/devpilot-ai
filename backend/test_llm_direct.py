"""
Direct LLM Service Test - Check if API calls are working
"""
from app.services.llm import LLMService

def test_direct_llm():
    """Test direct LLM call"""
    print("\n" + "="*70)
    print("TESTING DIRECT LLM API CALLS")
    print("="*70)
    
    llm = LLMService()
    
    # Test 1: Simple prompt
    print("\n1️⃣ TEST: Simple prompt with Mistral")
    response = llm.generate(
        prompt="What is 2+2?",
        provider="mistral",
        model="mistral-large-latest",
        temperature=0.3,
        max_tokens=100
    )
    
    print(f"✅ Success: {response.success}")
    print(f"📝 Content: {response.content[:100] if response.content else 'EMPTY'}")
    print(f"⏱️ Response time: {response.response_time_ms}ms")
    print(f"❌ Error: {response.error}")
    
    # Test 2: JSON response
    print("\n2️⃣ TEST: JSON response request")
    json_prompt = """Return ONLY valid JSON with this structure:
{
    "answer": "2+2 equals?",
    "result": 4
}"""
    
    response = llm.generate(
        prompt=json_prompt,
        provider="mistral",
        model="mistral-large-latest",
        temperature=0.1,
        max_tokens=100
    )
    
    print(f"✅ Success: {response.success}")
    print(f"📝 Content: {response.content[:200] if response.content else 'EMPTY'}")
    print(f"❌ Error: {response.error}")
    
    # Test 3: Debug-specific prompt
    print("\n3️⃣ TEST: Debug Error Analysis")
    debug_prompt = """Analyze this Python error and return ONLY valid JSON:

Error:
Traceback (most recent call last):
  File "script.py", line 6, in <module>
    print(items[10])
IndexError: list index out of range

Code context:
items = [1, 2, 3]
print(items[10])

Return JSON with:
{
    "root_cause": "...",
    "why_it_happened": "...",
    "solution": "..."
}"""
    
    response = llm.generate(
        prompt=debug_prompt,
        provider="mistral",
        model="mistral-large-latest",
        temperature=0.2,
        max_tokens=300
    )
    
    print(f"✅ Success: {response.success}")
    print(f"📝 Content (first 300 chars):\n{response.content[:300] if response.content else 'EMPTY'}")
    print(f"❌ Error: {response.error}")
    
    # Test 4: Try Groq (fastest)
    print("\n4️⃣ TEST: Groq provider (fastest)")
    response = llm.generate(
        prompt="What is Python IndexError?",
        provider="groq",
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=150
    )
    
    print(f"✅ Success: {response.success}")
    print(f"📝 Content: {response.content[:100] if response.content else 'EMPTY'}")
    print(f"⏱️ Response time: {response.response_time_ms}ms")
    print(f"❌ Error: {response.error}")
    
    # Test 5: Check provider status
    print("\n5️⃣ TEST: Provider status check")
    status = llm.status()
    print(f"Default provider: {status['default_provider']}")
    print(f"Working providers: {status['working_providers']}")
    for provider, info in status['providers'].items():
        working_count = len(info['working_models'])
        print(f"  {provider}: {working_count} working models")

if __name__ == "__main__":
    test_direct_llm()
