# Enhanced RAG Features Documentation

## Overview

The Legal Research RAG system has been enhanced with advanced query capabilities that go beyond simple semantic search. This document describes all available features and how to use them.

---

## 🆕 New Features

### 1. **Case Summarization** 📄

Generate comprehensive summaries of specific cases by case ID or name.

**Function:** `summarize_case(case_identifier)`

**Parameters:**
- `case_identifier`: Case name (e.g., "SC_0001") or CNR number

**Returns:**
```python
{
    "case_name": "Cleaned case name",
    "case_name_raw": "Original case name from database",
    "cnr": "Case CNR number",
    "disposal_nature": "Appeal allowed/dismissed/etc.",
    "summary": "Generated summary with Facts, Issues, Holding, Reasoning, Outcome",
    "chunks_used": 10,
    "total_chunks": 15
}
```

**Example Usage:**
```python
from rag import summarize_case

result = summarize_case("SC_0001")
print(result["summary"])
```

**Summary Structure:**
- **Facts**: Parties, events, lower court decisions
- **Legal Issues**: Questions the court addressed
- **Holding**: What the court decided
- **Reasoning**: Why the court decided this way
- **Outcome**: Final disposition

---

### 2. **Find Similar Cases** 🔍

Discover cases with similar legal issues, facts, or reasoning.

**Function:** `find_similar_cases(case_identifier, k=5, include_source=False)`

**Parameters:**
- `case_identifier`: Source case name or CNR
- `k`: Number of similar cases to find (default: 5)
- `include_source`: Include source case in results (default: False)

**Returns:**
```python
{
    "source_case": "Source case name",
    "source_cnr": "Source CNR",
    "similar_cases": [
        {
            "case_name": "Similar case name",
            "chunks": [...],  # Matching chunks
            "disposal_nature": "Outcome",
            "cnr": "CNR number"
        },
        ...
    ]
}
```

**Example Usage:**
```python
from rag import find_similar_cases

result = find_similar_cases("SC_0001", k=5)
for case in result["similar_cases"]:
    print(f"{case['case_name']}: {len(case['chunks'])} matching chunks")
```

**Use Cases:**
- Find precedents with similar fact patterns
- Identify cases on the same legal doctrine
- Track judicial reasoning patterns
- Build citation networks

---

### 3. **Metadata Filtering** 🎯

Filter cases by outcome, date, or other metadata during retrieval.

**Function:** `retrieve(query, k=5, filters=None, diverse=True)`

**Parameters:**
- `query`: Search query text (or None for metadata-only)
- `k`: Number of chunks to retrieve
- `filters`: Dictionary of metadata filters
- `diverse`: Limit to 2 chunks per case (default: True)

**Available Filters:**
- `disposal_nature`: Filter by outcome
  - "Appeal allowed"
  - "Appeal dismissed"
  - "Petition allowed"
  - "Petition dismissed"
- `case_name`: Exact case name match
- `cnr`: Filter by CNR number

**Example Usage:**
```python
from rag import retrieve

# Find constitutional rights cases where appeals were allowed
chunks = retrieve(
    query="constitutional rights",
    k=5,
    filters={"disposal_nature": "Appeal allowed"}
)

# Metadata-only search (no semantic query)
chunks = retrieve(
    query=None,
    k=10,
    filters={"disposal_nature": "Petition dismissed"}
)
```

---

### 4. **Get Case by Name** 📚

Retrieve all chunks from a specific case.

**Function:** `get_case_by_name(case_identifier, max_chunks=None)`

**Parameters:**
- `case_identifier`: Case name or CNR
- `max_chunks`: Limit number of chunks (None = all)

**Returns:** List of chunks sorted by chunk number

**Example Usage:**
```python
from rag import get_case_by_name

chunks = get_case_by_name("SC_0001", max_chunks=10)
print(f"Case has {len(chunks)} chunks")
for chunk in chunks:
    print(f"Chunk {chunk['chunk_number']}: {chunk['text'][:100]}...")
```

---

### 5. **Enhanced Generate Function** 💬

The main query function now supports filters and different query types.

**Function:** `generate(query, k=5, filters=None, query_type="general")`

**Parameters:**
- `query`: User's legal research question
- `k`: Number of chunks to retrieve
- `filters`: Optional metadata filters
- `query_type`: "general", "summarize", or "similar"

**Example Usage:**
```python
from rag import generate

# Query with outcome filter
result = generate(
    query="What are the grounds for appeal?",
    k=5,
    filters={"disposal_nature": "Appeal allowed"}
)

print(result["answer"])
for source in result["sources"]:
    print(f"- {source['case_name']}")
```

---

## 🎨 Streamlit UI Features

### Query Modes

The enhanced Streamlit app (`app.py`) now has 4 modes:

#### 1. **💬 Chat Mode** (Default)
- Ask legal questions
- Get answers with case citations
- Handles casual conversation
- Optional outcome filtering

#### 2. **📄 Summarize Case Mode**
- Enter case ID or name
- Get structured summary
- See outcome and metadata
- View chunks analyzed

#### 3. **🔍 Find Similar Cases Mode**
- Enter source case
- Find related cases
- See matching chunks
- Compare outcomes

#### 4. **🎯 Advanced Search Mode**
- Query with filters
- Filter by outcome
- Targeted retrieval
- Precise results

### Configuration Options

**Sidebar Controls:**
- **Query Mode**: Select mode from dropdown
- **Top K chunks**: Adjust retrieval count (1-20)
- **Filter by Outcome**: Filter cases by disposition
- **Clear Chat**: Reset conversation
- **Download PDF**: Export conversation

---

## 📊 Query Examples

### Example 1: Case Summarization
```
Mode: 📄 Summarize Case
Input: SC_0025

Output:
- Case Name: [Cleaned name]
- Outcome: Appeal dismissed
- Summary with Facts, Issues, Holding, Reasoning, Outcome
```

### Example 2: Find Similar Cases
```
Mode: 🔍 Find Similar Cases
Input: SC_0001

Output:
- Source: [Case name]
- 5 similar cases with:
  - Case names
  - Outcomes
  - Matching chunk counts
  - Sample excerpts
```

### Example 3: Filtered Query
```
Mode: 🎯 Advanced Search
Filter: Appeal allowed
Input: What are precedents on due process?

Output:
- Answer citing only appeal-allowed cases
- Sources from filtered results
```

### Example 4: Comparative Analysis
```python
# In Python script
from rag import summarize_case

case1 = summarize_case("SC_0001")
case2 = summarize_case("SC_0010")

# Compare summaries, outcomes, reasoning
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_enhanced_rag.py
```

**Test Coverage:**
1. Case summarization
2. Similar case finding
3. Metadata filtering
4. Enhanced queries
5. Get case by name
6. Comparative analysis

---

## 🔧 Technical Details

### Enhanced Retrieval
- Supports both semantic and metadata queries
- Diversity control (max 2 chunks per case)
- Flexible filtering system
- Efficient ChromaDB queries

### Case Summarization
- Uses up to 10 chunks for context
- Structured output format
- Handles incomplete excerpts
- Low temperature (0.2) for accuracy

### Similarity Search
- Concatenates source case chunks
- Semantic similarity via embeddings
- Groups results by case
- Ranked by relevance

### Metadata System
- `case_name`: Full case name
- `cnr`: Case CNR number
- `disposal_nature`: Outcome
- `chunk_number`: Position in case
- `total_chunks`: Total chunks in case

---

## 🚀 Future Enhancements

Potential additions:
- **Legal issue tagging**: Automatic categorization
- **Citation network analysis**: Track case citations
- **Temporal queries**: Filter by date ranges
- **Judge-based search**: Find opinions by judge
- **Multi-hop reasoning**: Chain multiple queries
- **Comparative reports**: Side-by-side case analysis
- **Topic clustering**: Group similar cases
- **Entity extraction**: Parties, statutes, articles

---

## 📝 API Reference

### Core Functions

```python
# Retrieval
retrieve(query, k=5, filters=None, diverse=True) -> List[dict]

# Case operations
get_case_by_name(case_identifier, max_chunks=None) -> List[dict]
summarize_case(case_identifier) -> dict
find_similar_cases(case_identifier, k=5, include_source=False) -> dict

# Generation
generate(query, k=5, filters=None, query_type="general") -> dict

# Utilities
clean_case_name(case_name) -> str
```

### Return Types

**Chunk Dictionary:**
```python
{
    "text": str,
    "case_name": str,
    "case_name_display": str,  # Cleaned name
    "chunk_number": int,
    "total_chunks": int,
    "disposal_nature": str,
    "cnr": str,
    "ref_number": int  # Added during generation
}
```

---

## 💡 Best Practices

1. **Use summarization** for understanding specific cases
2. **Use similarity search** to find precedents
3. **Use filters** when you know the outcome you want
4. **Combine modes** for comprehensive research
5. **Check sources** - always verify against original judgments
6. **Export conversations** for documentation

---

## ⚖️ Disclaimer

This is an AI-powered research aid based on retrieved excerpts. It is:
- ✅ Good for: Initial research, precedent discovery, case summaries
- ❌ Not for: Legal advice, final citations, court submissions

Always consult qualified legal professionals and verify against original judgments.

---

## 📞 Support

For issues or questions:
1. Check test suite: `python test_enhanced_rag.py`
2. Review this documentation
3. Check source code comments in `rag.py`
4. Test with known cases (SC_0001, SC_0010, etc.)
