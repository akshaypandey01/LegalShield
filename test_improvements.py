"""Test the quality improvements: diversity, clean names, CNR"""
import os
os.environ['HF_HOME'] = 'D:\\huggingface_cache'

from rag import retrieve, generate, clean_case_name

# Test query
query = "What are the grounds for granting special leave to appeal?"

print("=" * 80)
print(f"Query: {query}")
print("=" * 80)

# Test retrieve with diversity
print("\n1. TESTING DIVERSITY RETRIEVAL (max 2 chunks per case):")
print("-" * 80)
results = retrieve(query, k=5)
print(f"Retrieved {len(results)} chunks")

# Check diversity - count chunks per case
case_counts = {}
for r in results:
    case_name = r['case_name']
    case_counts[case_name] = case_counts.get(case_name, 0) + 1

print(f"\nChunks per case (should be max 2):")
for case, count in case_counts.items():
    print(f"  {case}: {count} chunks")
    if count > 2:
        print("    ⚠️  WARNING: More than 2 chunks from same case!")

# Test clean_case_name
print("\n2. TESTING CASE NAME CLEANING:")
print("-" * 80)
for r in results:
    original = r['case_name']
    cleaned = clean_case_name(original)
    if original != cleaned:
        print(f"Original: {original[:80]}")
        print(f"Cleaned:  {cleaned}")
        print()

# Test CNR display
print("\n3. TESTING CNR METADATA:")
print("-" * 80)
for i, r in enumerate(results, 1):
    cnr = r.get('cnr', 'Not available')
    case_name = clean_case_name(r['case_name'])
    print(f"{i}. {case_name}")
    print(f"   CNR: {cnr}")

# Test generate with improved prompt
print("\n4. TESTING IMPROVED GENERATION (grouped by case, temp=0.15):")
print("-" * 80)
answer = generate(query, k=5)
print(answer)

print("\n" + "=" * 80)
print("✓ Test complete")
