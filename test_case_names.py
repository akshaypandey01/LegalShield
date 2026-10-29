"""Test case name extraction - print 10 examples"""
import os
os.environ['HF_HOME'] = 'D:\\huggingface_cache'

from load_data import load_cases

print("=" * 80)
print("TESTING CASE NAME EXTRACTION")
print("=" * 80)

# Load 10 cases as a quick test
cases = load_cases(10)

print("\n" + "=" * 80)
print("EXTRACTED CASE NAMES (10 samples):")
print("=" * 80)

for i, case in enumerate(cases, 1):
    print(f"\n{i}. {case['case_name']}")
    if case.get('cnr'):
        print(f"   CNR: {case['cnr']}")
    if case.get('year'):
        print(f"   Year: {case['year']}")
    # Show first 100 chars of text to see if extraction makes sense
    print(f"   Preview: {case['text'][:100]}...")

print("\n" + "=" * 80)
print("✓ Test complete")
