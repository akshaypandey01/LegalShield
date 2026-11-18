"""
Quick test for enhanced RAG features (no LLM calls).
Tests retrieval and data access functions only.
"""

from rag import retrieve, get_case_by_name, find_similar_cases
import chromadb


def test_basic_retrieval():
    """Test basic retrieval still works."""
    print("\n" + "="*80)
    print("TEST 1: Basic Retrieval")
    print("="*80)
    
    chunks = retrieve("constitutional rights", k=5)
    print(f"✓ Retrieved {len(chunks)} chunks")
    
    if chunks:
        print(f"  Sample case: {chunks[0]['case_name']}")
        print(f"  Outcome: {chunks[0]['disposal_nature']}")
        print(f"  Text preview: {chunks[0]['text'][:100]}...")
    
    return len(chunks) > 0


def test_metadata_filtering():
    """Test metadata filtering."""
    print("\n" + "="*80)
    print("TEST 2: Metadata Filtering")
    print("="*80)
    
    # First, let's see what disposal natures exist
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="legal_cases")
    sample = collection.get(limit=100)
    
    outcomes = set()
    for meta in sample['metadatas']:
        outcomes.add(meta.get('disposal_nature', 'Unknown'))
    
    print(f"Available outcomes in database: {outcomes}")
    
    # Test with a filter if outcomes exist
    if len(outcomes) > 1:
        outcome = list(outcomes)[0]
        print(f"\n  Testing filter: disposal_nature = '{outcome}'")
        
        chunks = retrieve("rights", k=5, filters={"disposal_nature": outcome})
        print(f"  ✓ Retrieved {len(chunks)} chunks with outcome '{outcome}'")
        
        if chunks:
            # Verify all have correct outcome
            correct = all(c['disposal_nature'] == outcome for c in chunks)
            print(f"  ✓ Filter correctness: {correct}")
            return correct
    
    return True


def test_get_case_by_name():
    """Test retrieving a full case."""
    print("\n" + "="*80)
    print("TEST 3: Get Case by Name")
    print("="*80)
    
    # First get a case name from the database
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="legal_cases")
    sample = collection.get(limit=5)
    
    if not sample['ids']:
        print("  ✗ No cases in database")
        return False
    
    # Use the first case name
    test_case_name = sample['metadatas'][0]['case_name']
    print(f"  Testing with case: {test_case_name[:50]}...")
    
    chunks = get_case_by_name(test_case_name)
    
    if chunks:
        print(f"  ✓ Retrieved {len(chunks)} chunks from case")
        print(f"  ✓ First chunk number: {chunks[0]['chunk_number']}")
        print(f"  ✓ Last chunk number: {chunks[-1]['chunk_number']}")
        
        # Verify they're from the same case
        same_case = all(c['case_name'] == test_case_name for c in chunks)
        print(f"  ✓ All chunks from same case: {same_case}")
        
        # Verify sorted by chunk number
        sorted_correctly = all(
            chunks[i]['chunk_number'] <= chunks[i+1]['chunk_number']
            for i in range(len(chunks)-1)
        )
        print(f"  ✓ Sorted by chunk number: {sorted_correctly}")
        
        return same_case and sorted_correctly
    else:
        print("  ✗ No chunks retrieved")
        return False


def test_database_stats():
    """Show database statistics."""
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="legal_cases")
    
    # Get total count
    all_data = collection.get(limit=10000)
    total_chunks = len(all_data['ids'])
    
    print(f"  Total chunks: {total_chunks}")
    
    # Count unique cases
    unique_cases = set(meta['case_name'] for meta in all_data['metadatas'])
    print(f"  Unique cases: {len(unique_cases)}")
    
    # Count outcomes
    outcomes = {}
    for meta in all_data['metadatas']:
        outcome = meta.get('disposal_nature', 'Unknown')
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    
    print(f"\n  Outcomes distribution:")
    for outcome, count in sorted(outcomes.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {outcome}: {count} chunks")
    
    # Sample case names
    print(f"\n  Sample case names:")
    for i, case in enumerate(list(unique_cases)[:5], 1):
        print(f"    {i}. {case[:80]}...")
    
    return True


def main():
    """Run all quick tests."""
    print("\n" + "🚀"*40)
    print("ENHANCED RAG - QUICK TEST SUITE (No LLM)")
    print("🚀"*40)
    
    results = []
    
    try:
        # Show database stats first
        test_database_stats()
        
        # Run retrieval tests
        results.append(("Basic Retrieval", test_basic_retrieval()))
        results.append(("Metadata Filtering", test_metadata_filtering()))
        results.append(("Get Case by Name", test_get_case_by_name()))
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        for test_name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {test_name}")
        
        passed_count = sum(1 for _, passed in results if passed)
        print(f"\n  Total: {passed_count}/{len(results)} tests passed")
        
        if passed_count == len(results):
            print("\n  🎉 All tests passed!")
        else:
            print("\n  ⚠️ Some tests failed")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
