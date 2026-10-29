"""
Test script to verify conversational responses don't leak prompts or hallucinate turns.
Run multiple iterations of each test case to catch intermittent issues.
"""

import sys
from ollama import Client

# Configuration
OLLAMA_MODEL = "phi3:mini"
OLLAMA_HOST = "http://localhost:11434"


def sanitize_conversational_response(text):
    """
    Remove leaked instructions or fabricated conversation turns from LLM output.
    """
    leak_markers = [
        "User message:",
        "Your response:",
        "\nUser:",
        "Guidelines:",
        "Respond naturally",
        "Keep it brief",
        "For greetings:",
        "For thanks:",
        "casual message"
    ]
    
    first_leak_pos = len(text)
    for marker in leak_markers:
        pos = text.find(marker)
        if pos != -1 and pos < first_leak_pos:
            first_leak_pos = pos
    
    if first_leak_pos < len(text):
        text = text[:first_leak_pos]
    
    text = text.strip()
    return text


def generate_conversational_response(user_message):
    """
    Generate a conversational response for non-legal queries using the LLM.
    """
    prompt = f"""You are a friendly legal research assistant. The user sent you a casual message (not a legal query).

Respond naturally and helpfully. Keep it brief (1-3 sentences).

Guidelines:
- For greetings: Be welcoming and explain you can help with legal research
- For "what can you do": Explain you search court cases and provide citations
- For thanks: Acknowledge warmly
- For goodbyes: Be friendly
- For other casual messages: Respond naturally while steering toward legal assistance

User message: {user_message}

Your response:"""
    
    client = Client(host=OLLAMA_HOST)
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_predict": 100,
            "stop": [
                "User message:",
                "Your response:",
                "\nUser:",
                "\nUser message:",
                "Guidelines:",
                "\n\n\n"
            ]
        }
    )
    
    answer = response['message']['content']
    sanitized = sanitize_conversational_response(answer)
    
    return sanitized


def check_for_leaks(response_text):
    """Check if response contains leaked instructions or fabricated turns."""
    leak_indicators = [
        "User message:",
        "Your response:",
        "Guidelines:",
        "Respond naturally",
        "Keep it brief",
        "For greetings:",
        "casual message"
    ]
    
    found_leaks = []
    for indicator in leak_indicators:
        if indicator in response_text:
            found_leaks.append(indicator)
    
    return found_leaks


def test_message(message, iterations=6):
    """Test a single message multiple times."""
    print(f"\n{'='*80}")
    print(f"Testing: '{message}'")
    print(f"Iterations: {iterations}")
    print('='*80)
    
    all_passed = True
    
    for i in range(iterations):
        print(f"\n--- Iteration {i+1}/{iterations} ---")
        
        try:
            response = generate_conversational_response(message)
            print(f"Response: {response}")
            
            # Check length
            word_count = len(response.split())
            token_estimate = len(response.split()) * 1.3  # rough estimate
            print(f"Length: {word_count} words (~{token_estimate:.0f} tokens)")
            
            # Check for leaks
            leaks = check_for_leaks(response)
            if leaks:
                print(f"⚠️  LEAK DETECTED: {leaks}")
                all_passed = False
            else:
                print("✓ No leaks detected")
            
            # Check if response is reasonable length (not too long)
            if word_count > 60:
                print(f"⚠️  Response too long ({word_count} words, expected < 60)")
                all_passed = False
            else:
                print(f"✓ Length appropriate")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            all_passed = False
    
    return all_passed


def main():
    """Run test suite."""
    print("="*80)
    print("CONVERSATIONAL RESPONSE TEST SUITE")
    print("="*80)
    print(f"Model: {OLLAMA_MODEL}")
    print(f"Host: {OLLAMA_HOST}")
    print(f"Stop sequences: User message:, Your response:, \\nUser:, Guidelines:")
    print(f"Max tokens: 100")
    
    # Test cases
    test_cases = [
        "Hi",
        "Hello",
        "Hey there",
        "What can you do?",
        "Tell me about yourself",
        "Thanks",
        "Thank you so much!",
        "Goodbye"
    ]
    
    results = {}
    
    for test_case in test_cases:
        passed = test_message(test_case, iterations=6)
        results[test_case] = passed
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    all_passed = True
    for test_case, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{status}: '{test_case}'")
        if not passed:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    else:
        print("❌❌❌ SOME TESTS FAILED ❌❌❌")
    print("="*80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
