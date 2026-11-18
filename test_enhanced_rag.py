"""
Test script for enhanced RAG features:
- Case summarization
- Find similar cases
- Metadata filtering
- Enhanced retrieval
"""

from rag import (
    summarize_case, 
    find_similar_cases, 
    retrieve, 
    generate,
    get_case_by_name
)
import json


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_case_summarization():
    """Test case summarization functionality."""
    print_header("TEST 1: CASE SUMMARIZATION")
    
    # Test with a case name pattern
    test_cases = ["SC_0001", "SC_0010", "SC_0025"]
    
    for case_id in test_cases:
        print(f"\n📄 Summarizing case: {case_id}")
        print("-" * 80)
        
        result = summarize_case(case_id)
        
        if "error" in result:
            print(f"❌ Error: {result['summary']}")
        else:
            print(f"**Case Name:** {result['case_name']}")
            if result.get('cnr'):
                print(f"**CNR:** {result['cnr']}")
            print(f"**Outcome:** {result['disposal_nature']}")
            print(f"**Chunks Used:** {result['chunks_used']}/{result['total_chunks']}")
            print(f"\n**Summary:**\n{result['summary']}")
        
        print("\n")


def test_similar_cases():
    """Test finding similar cases."""
    print_header("TEST 2: FIND SIMILAR CASES")
    
    # Test finding cases similar to a specific case
    source_case = "SC_0001"
    
    print(f"\n🔍 Finding cases similar to: {source_case}")
    print("-" * 80)
    
    result = find_similar_cases(source_case, k=5, include_source=False)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"**Source Case:** {result['source_case']}")
        if result.get('source_cnr'):
            print(f"**Source CNR:** {result['source_cnr']}")
        
        print(f"\n**Found {len(result['similar_cases'])} similar cases:**\n")
        
        for i, case in enumerate(result['similar_cases'], 1):
            print(f"{i}. {case['case_name']}")
            print(f"   Outcome: {case['disposal_nature']}")
            if case['cnr']:
                print(f"   CNR: {case['cnr']}")
            print(f"   Matching chunks: {len(case['chunks'])}")
            print(f"   Sample text: {case['chunks'][0]['text'][:200]}...")
            print()


def test_metadata_filtering():
    """Test metadata filtering in retrieval."""
    print_header("TEST 3: METADATA FILTERING")
    
    # Test 1: Filter by disposal nature
    print("\n🔎 Query: Cases where appeals were allowed")
    print("-" * 80)
    
    chunks = retrieve(
        query="constitutional rights",
        k=5,
        filters={"disposal_nature": "Appeal allowed"}
    )
    
    print(f"Found {len(chunks)} chunks from appeal-allowed cases:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"{i}. {chunk['case_name']}")
        print(f"   Outcome: {chunk['disposal_nature']}")
        print(f"   Text: {chunk['text'][:150]}...")
        print()
    
    # Test 2: General query with outcome focus
    print("\n🔎 Query: Constitutional rights in dismissed appeals")
    print("-" * 80)
    
    chunks = retrieve(
        query="constitutional rights",
        k=5,
        filters={"disposal_nature": "Appeal dismissed"}
    )
    
    print(f"Found {len(chunks)} chunks from dismissed appeals:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"{i}. {chunk['case_name']}")
        print(f"   Outcome: {chunk['disposal_nature']}")
        print()


def test_enhanced_queries():
    """Test enhanced query capabilities."""
    print_header("TEST 4: ENHANCED QUERIES")
    
    # Test query patterns
    queries = [
        {
            "query": "What are the key precedents on freedom of speech?",
            "description": "General legal question"
        },
        {
            "query": "Cases involving police misconduct",
            "description": "Topic-based search",
            "filters": {"disposal_nature": "Appeal allowed"}
        }
    ]
    
    for test in queries:
        print(f"\n📝 {test['description']}")
        print(f"Query: \"{test['query']}\"")
        print("-" * 80)
        
        filters = test.get('filters', None)
        result = generate(test['query'], k=5, filters=filters)
        
        print(f"\n**Answer:**\n{result['answer']}\n")
        print(f"**Sources:** {len(result['sources'])} chunks from "
              f"{len(set(s['case_name'] for s in result['sources']))} cases")
        print()


def test_get_case_by_name():
    """Test retrieving all chunks from a specific case."""
    print_header("TEST 5: GET CASE BY NAME")
    
    case_id = "SC_0005"
    print(f"\n📚 Retrieving all chunks from: {case_id}")
    print("-" * 80)
    
    chunks = get_case_by_name(case_id)
    
    if not chunks:
        print(f"❌ Case not found: {case_id}")
    else:
        print(f"**Case Name:** {chunks[0]['case_name']}")
        print(f"**CNR:** {chunks[0].get('cnr', 'N/A')}")
        print(f"**Outcome:** {chunks[0]['disposal_nature']}")
        print(f"**Total Chunks:** {len(chunks)}")
        
        print(f"\n**First 3 chunks:**\n")
        for chunk in chunks[:3]:
            print(f"Chunk {chunk['chunk_number']}:")
            print(f"{chunk['text'][:300]}...")
            print()


def test_comparative_analysis():
    """Test comparing multiple cases."""
    print_header("TEST 6: COMPARATIVE ANALYSIS")
    
    # Simulate comparing two cases
    case1 = "SC_0001"
    case2 = "SC_0010"
    
    print(f"\n⚖️ Comparing cases: {case1} vs {case2}")
    print("-" * 80)
    
    # Get summaries of both cases
    summary1 = summarize_case(case1)
    summary2 = summarize_case(case2)
    
    if "error" not in summary1 and "error" not in summary2:
        print(f"\n**Case 1: {summary1['case_name']}**")
        print(f"Outcome: {summary1['disposal_nature']}")
        print(f"Summary excerpt: {summary1['summary'][:300]}...")
        
        print(f"\n**Case 2: {summary2['case_name']}**")
        print(f"Outcome: {summary2['disposal_nature']}")
        print(f"Summary excerpt: {summary2['summary'][:300]}...")
    else:
        print("❌ One or both cases not found")


def main():
    """Run all tests."""
    print("\n" + "🚀" * 40)
    print("ENHANCED RAG SYSTEM - COMPREHENSIVE TEST SUITE")
    print("🚀" * 40)
    
    try:
        # Run all test suites
        test_case_summarization()
        test_similar_cases()
        test_metadata_filtering()
        test_enhanced_queries()
        test_get_case_by_name()
        test_comparative_analysis()
        
        print_header("✅ ALL TESTS COMPLETED")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
