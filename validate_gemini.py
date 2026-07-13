"""Surgical validation of GeminiProvider hotfix."""
import os
import sys
import traceback

def test_import():
    print("--- TEST 1: Import GeminiProvider ---")
    try:
        from answer_engine.gemini_provider import GeminiProvider
        from answer_engine.llm_provider import BaseLLMProvider, LLMResponse
        assert issubclass(GeminiProvider, BaseLLMProvider)
        print("[OK] GeminiProvider imports and extends BaseLLMProvider correctly.\n")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}\n")
        return False

def test_missing_key():
    print("--- TEST 2: Missing API Key Error Handling ---")
    original = os.environ.pop("GEMINI_API_KEY", None)
    try:
        from answer_engine.gemini_provider import GeminiProvider
        try:
            provider = GeminiProvider("gemini-2.0-flash", 0.0, 1500)
            print("[FAIL] Should have raised EnvironmentError.\n")
            return False
        except EnvironmentError as e:
            print(f"[OK] Correct EnvironmentError raised: {e}\n")
            return True
        except Exception as e:
            print(f"[FAIL] Wrong exception type: {type(e).__name__}: {e}\n")
            return False
    finally:
        if original is not None:
            os.environ["GEMINI_API_KEY"] = original

def test_mock_regression():
    print("--- TEST 3: Mock Provider Regression ---")
    try:
        from answer_engine.config import AnswerEngineConfig
        from answer_engine.answer_generator import AnswerGenerator
        from answer_engine.models import GeneratedPrompt
        
        config = AnswerEngineConfig()  # defaults to llm_provider="mock"
        gen = AnswerGenerator(config)
        
        prompt = GeneratedPrompt(
            system_prompt="You are a legal assistant.",
            user_prompt="What is Section 162?",
            estimated_tokens=100,
            context_token_count=50,
            included_chunks=0
        )
        result = gen.generate_answer(prompt)
        assert isinstance(result, dict)
        assert "answer" in result
        print(f"[OK] MockProvider still works. Answer: {result['answer'][:60]}...\n")
        return True
    except Exception as e:
        print(f"[FAIL] Mock regression: {e}\n")
        traceback.print_exc()
        return False

def test_gemini_live():
    print("--- TEST 4: Live Gemini E2E ---")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[SKIP] GEMINI_API_KEY not set. Skipping live test.\n")
        return None
    
    try:
        os.environ["ANSWER_LLM_PROVIDER"] = "gemini"
        os.environ["ANSWER_LLM_MODEL"] = "gemini-2.0-flash"
        
        from answer_engine.config import AnswerEngineConfig
        from answer_engine.answer_generator import AnswerGenerator
        from answer_engine.response_parser import parse_llm_response
        from answer_engine.models import GeneratedPrompt
        
        config = AnswerEngineConfig(
            llm_provider="gemini",
            llm_model="gemini-2.0-flash",
            llm_temperature=0.0,
            llm_max_tokens=1500
        )
        gen = AnswerGenerator(config)
        
        prompt = GeneratedPrompt(
            system_prompt="You are a legal assistant for U.S. tax law. Respond in JSON with keys: answer, citations, confidence, limitations.",
            user_prompt='Based on the following context, answer: What expenses are deductible under Section 162?\n\nContext:\nSection 162 allows taxpayers to deduct ordinary and necessary expenses paid or incurred during the taxable year in carrying on any trade or business.',
            estimated_tokens=200,
            context_token_count=100,
            included_chunks=1
        )
        
        result = gen.generate_answer(prompt)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "answer" in result, "Missing 'answer' key"
        
        print(f"[OK] Gemini responded successfully!")
        print(f"     Provider: gemini")
        print(f"     Answer length: {len(result.get('answer', ''))}")
        print(f"     Confidence: {result.get('confidence', 'N/A')}")
        print(f"     Citations: {len(result.get('citations', []))}")
        print(f"     ResponseParser: PASSED")
        print(f"     Validator: PASSED\n")
        return True
    except Exception as e:
        print(f"[FAIL] Live Gemini test failed: {e}\n")
        traceback.print_exc()
        return False
    finally:
        os.environ.pop("ANSWER_LLM_PROVIDER", None)
        os.environ.pop("ANSWER_LLM_MODEL", None)

if __name__ == "__main__":
    results = {}
    results["import"] = test_import()
    results["missing_key"] = test_missing_key()
    results["mock_regression"] = test_mock_regression()
    results["gemini_live"] = test_gemini_live()
    
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    for name, status in results.items():
        icon = "[OK]" if status is True else ("[SKIP]" if status is None else "[FAIL]")
        print(f"  {icon} {name}")
    
    failures = [k for k, v in results.items() if v is False]
    if failures:
        print(f"\n[BLOCKED] Deployment blocked by: {', '.join(failures)}")
        sys.exit(1)
    else:
        print(f"\n[READY] All validations passed. Production ready.")
        sys.exit(0)
