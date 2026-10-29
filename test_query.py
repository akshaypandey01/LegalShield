from rag import generate

query = "What are the principles of natural justice in Indian law?"
print(f"Query: {query}\n")

result = generate(query, k=5)

print("=" * 80)
print("ANSWER:")
print("=" * 80)
print(result['answer'])

print("\n" + "=" * 80)
print("SOURCES:")
print("=" * 80)
for i, source in enumerate(result['sources'], 1):
    print(f"\n{i}. {source['case_name']}")
    print(f"   Chunk: {source['chunk_number']}")
    print(f"   Outcome: {source['disposal_nature']}")
    print(f"   Preview: {source['text'][:150]}...")
