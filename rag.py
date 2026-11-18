"""
RAG (Retrieval-Augmented Generation) for legal research.
Retrieves relevant case chunks and generates answers using Ollama.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from ollama import Client
import re

# Configuration
OLLAMA_MODEL = "phi3:mini"
OLLAMA_HOST = "http://localhost:11434"


def clean_case_name(case_name):
    """
    Clean OCR noise from case names.
    Remove running headers, cut at bracketed year/judge list, keep "X v. Y" format.
    
    Args:
        case_name: Raw case name from dataset
        
    Returns:
        Cleaned case name
    """
    if not case_name or case_name.strip() == "":
        return case_name
    
    # Remove running header patterns
    # Pattern: "1960 March 14. SUPREME COURT REPORTS (1950]"
    case_name = re.sub(r'\d{4}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d+\.', '', case_name)
    case_name = re.sub(r'SUPREME COURT REPORTS?', '', case_name, flags=re.IGNORECASE)
    case_name = re.sub(r'S\.?C\.?R\.?', '', case_name)
    case_name = re.sub(r'\[\d{4}\]', '', case_name)
    case_name = re.sub(r'\(\d{4}\)', '', case_name)
    
    # Cut at first bracketed content (judge names, citations)
    # Look for patterns like "(SHRI...", "[S. R. DAS...", etc.
    match = re.search(r'[\[\(][A-Z][A-Z\s\.,]+', case_name)
    if match:
        case_name = case_name[:match.start()].strip()
    
    # Remove page numbers and volume citations at the end
    case_name = re.sub(r'\s+\d+\s*$', '', case_name)
    
    # Clean up multiple spaces and special chars
    case_name = re.sub(r'\s+', ' ', case_name)
    case_name = case_name.strip(' .,;:-')
    
    # If too long (likely contains noise), try to extract "X v. Y" pattern
    if len(case_name) > 100:
        # Look for "X v. Y" or "X vs Y" pattern
        match = re.search(r'([A-Z][A-Za-z\s&\.,-]+?)\s+(?:v\.?|vs\.?|Vs\.?)\s+([A-Z][A-Za-z\s&\.,-]+?)(?:\s|$)', case_name)
        if match:
            case_name = f"{match.group(1).strip()} v. {match.group(2).strip()}"
    
    return case_name.strip()[:150]  # Cap length


def retrieve(query, k=5, filters=None, diverse=True):
    """
    Retrieve top-k most relevant chunks for a query with optional filtering.
    ALL retrieval must go through this function (for future audit logging).
    
    Args:
        query: Search query (text string or None for metadata-only search)
        k: Number of chunks to retrieve (default 5)
        filters: Dict of metadata filters (e.g., {"disposal_nature": "Appeal allowed"})
        diverse: If True, limit to max 2 chunks per case (default True)
        
    Returns:
        List of dicts with keys: text, case_name, chunk_number, disposal_nature, cnr
    """
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="legal_cases")
    
    # Prepare query parameters
    query_params = {"n_results": k * 2 if diverse else k}
    
    # Add metadata filter if provided
    if filters:
        query_params["where"] = filters
    
    # Perform query based on whether we have a text query or not
    if query:
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(query).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            **query_params
        )
    else:
        # Metadata-only query (no semantic search)
        results = collection.get(
            where=filters,
            limit=k * 2 if diverse else k
        )
        # Restructure results to match query format
        if results['ids']:
            results = {
                'documents': [results['documents']],
                'metadatas': [results['metadatas']],
                'ids': [results['ids']]
            }
        else:
            results = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
    
    # Format results with optional diversity (max 2 chunks per case)
    retrieved_chunks = []
    case_chunk_counts = {}
    
    if results['documents'] and len(results['documents']) > 0:
        for i in range(len(results['documents'][0])):
            case_name = results['metadatas'][0][i]['case_name']
            
            # Apply diversity constraint if enabled
            if diverse and case_chunk_counts.get(case_name, 0) >= 2:
                continue
            
            retrieved_chunks.append({
                "text": results['documents'][0][i],
                "case_name": case_name,
                "chunk_number": results['metadatas'][0][i]['chunk_number'],
                "total_chunks": results['metadatas'][0][i].get('total_chunks', 0),
                "disposal_nature": results['metadatas'][0][i].get('disposal_nature', 'Unknown'),
                "cnr": results['metadatas'][0][i].get('cnr', '')
            })
            
            case_chunk_counts[case_name] = case_chunk_counts.get(case_name, 0) + 1
            
            # Stop when we have k chunks
            if len(retrieved_chunks) >= k:
                break
    
    return retrieved_chunks


def get_case_by_name(case_identifier, max_chunks=None):
    """
    Retrieve all chunks from a specific case by case name or CNR.
    
    Args:
        case_identifier: Case name (exact or partial) or CNR number
        max_chunks: Maximum chunks to retrieve (None = all chunks)
        
    Returns:
        List of chunks from the case, or empty list if not found
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="legal_cases")
    
    # Try to get all documents and filter manually
    # ChromaDB's where clause has limited support for string matching
    all_results = collection.get(limit=10000)
    
    if not all_results['ids']:
        return []
    
    # Filter for matching case names or CNRs
    matching_chunks = []
    for i in range(len(all_results['ids'])):
        case_name = all_results['metadatas'][i]['case_name']
        cnr = all_results['metadatas'][i].get('cnr', '')
        
        # Check if identifier matches case name or CNR
        if (case_identifier == case_name or 
            case_identifier == cnr or
            case_identifier.lower() in case_name.lower()):
            matching_chunks.append({
                "text": all_results['documents'][i],
                "case_name": case_name,
                "chunk_number": all_results['metadatas'][i]['chunk_number'],
                "total_chunks": all_results['metadatas'][i].get('total_chunks', 0),
                "disposal_nature": all_results['metadatas'][i].get('disposal_nature', 'Unknown'),
                "cnr": cnr,
                "id": all_results['ids'][i]
            })
            
            # Stop if we have enough chunks
            if max_chunks and len(matching_chunks) >= max_chunks:
                break
    
    if not matching_chunks:
        return []
    
    # Sort by chunk number
    matching_chunks.sort(key=lambda x: x['chunk_number'])
    return matching_chunks


def find_similar_cases(case_identifier, k=5, include_source=False):
    """
    Find cases similar to a given case.
    
    Args:
        case_identifier: Case name or CNR to find similar cases for
        k: Number of similar cases to find
        include_source: If True, include the source case in results
        
    Returns:
        Dict with:
            - source_case: Name of the source case
            - similar_cases: List of similar case dicts with case_name, chunks, similarity
    """
    # Get chunks from the source case
    source_chunks = get_case_by_name(case_identifier, max_chunks=5)
    
    if not source_chunks:
        return {
            "source_case": case_identifier,
            "similar_cases": [],
            "error": "Source case not found"
        }
    
    source_case_name = source_chunks[0]['case_name']
    
    # Use first few chunks to find similar cases
    # Concatenate chunk texts for richer semantic search
    query_text = " ".join([chunk['text'] for chunk in source_chunks[:3]])
    
    # Retrieve similar chunks
    similar_chunks = retrieve(query_text, k=k*3, diverse=True)
    
    # Group by case and calculate similarity
    cases_dict = {}
    for chunk in similar_chunks:
        case_name = chunk['case_name']
        
        # Skip source case unless explicitly requested
        if not include_source and case_name == source_case_name:
            continue
        
        if case_name not in cases_dict:
            cases_dict[case_name] = {
                "case_name": case_name,
                "chunks": [],
                "disposal_nature": chunk['disposal_nature'],
                "cnr": chunk['cnr']
            }
        
        cases_dict[case_name]['chunks'].append(chunk)
    
    # Sort by number of matching chunks (relevance proxy)
    similar_cases = sorted(
        cases_dict.values(),
        key=lambda x: len(x['chunks']),
        reverse=True
    )[:k]
    
    return {
        "source_case": source_case_name,
        "source_cnr": source_chunks[0].get('cnr', ''),
        "similar_cases": similar_cases
    }


def summarize_case(case_identifier):
    """
    Generate a comprehensive summary of a specific case.
    
    Args:
        case_identifier: Case name or CNR
        
    Returns:
        Dict with:
            - case_name: Name of the case
            - summary: Generated summary
            - metadata: Case metadata (CNR, outcome, etc.)
            - chunks_used: Number of chunks used
    """
    # Retrieve all chunks from the case
    chunks = get_case_by_name(case_identifier)
    
    if not chunks:
        return {
            "case_name": case_identifier,
            "summary": "Case not found in database.",
            "error": "not_found"
        }
    
    case_name = chunks[0]['case_name']
    case_name_display = clean_case_name(case_name)
    
    # Limit to first 10 chunks for reasonable summary length
    chunks_to_use = chunks[:10]
    
    # Concatenate chunk texts
    full_text = "\n\n".join([chunk['text'] for chunk in chunks_to_use])
    
    # Create summary prompt
    prompt = f"""You are a legal research assistant. Summarize the following case excerpts from {case_name_display}.

INSTRUCTIONS:
1. Provide a structured summary with these sections:
   - **Facts**: What happened (parties, events, lower court decisions)
   - **Legal Issues**: What questions the court addressed
   - **Holding**: What the court decided
   - **Reasoning**: Why the court decided this way
   - **Outcome**: Final disposition

2. Use ONLY information from the provided excerpts
3. If a section cannot be determined from excerpts, state "Not shown in excerpts"
4. Be concise but complete
5. Use legal terminology appropriately

Case Excerpts:
{full_text}

Summary:"""
    
    print(f"Generating summary for: {case_name_display}")
    
    # Call Ollama
    client = Client(host=OLLAMA_HOST)
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2}
    )
    
    summary = response['message']['content']
    
    return {
        "case_name": case_name_display,
        "case_name_raw": case_name,
        "cnr": chunks[0].get('cnr', ''),
        "disposal_nature": chunks[0].get('disposal_nature', 'Unknown'),
        "summary": summary,
        "chunks_used": len(chunks_to_use),
        "total_chunks": chunks[0].get('total_chunks', len(chunks))
    }


def generate(query, k=5, filters=None, query_type="general"):
    """
    Generate an answer to the query using retrieved chunks and Ollama.
    Uses consistent case names throughout answer and sources.
    
    Args:
        query: User's legal research question
        k: Number of chunks to retrieve (default 5)
        filters: Optional metadata filters (e.g., {"disposal_nature": "Appeal allowed"})
        query_type: Type of query - "general", "summarize", "similar" (default "general")
        
    Returns:
        Dict with keys: answer, sources (list of retrieved chunks with cleaned names)
    """
    print(f"Retrieving relevant cases for: '{query}'")
    
    # Retrieve relevant chunks with diversity
    chunks = retrieve(query, k=k, filters=filters, diverse=True)
    
    if not chunks:
        return {
            "answer": "No relevant cases found in the database.",
            "sources": []
        }
    
    # Clean case names ONCE - use same name everywhere
    for chunk in chunks:
        chunk['case_name_display'] = clean_case_name(chunk['case_name'])
    
    # Create numbered references for each chunk
    for i, chunk in enumerate(chunks, 1):
        chunk['ref_number'] = i
    
    print(f"Retrieved {len(chunks)} chunks from {len(set(c['case_name'] for c in chunks))} cases")
    
    # Build context from chunks, grouped by case
    cases_dict = {}
    for chunk in chunks:
        display_name = chunk['case_name_display']
        if display_name not in cases_dict:
            cases_dict[display_name] = []
        cases_dict[display_name].append(chunk)
    
    context_parts = []
    for case_name, case_chunks in cases_dict.items():
        # Use first chunk's reference numbers
        refs = ", ".join([f"[{c['ref_number']}]" for c in case_chunks])
        case_context = f"{refs} {case_name}\n"
        if case_chunks[0]['disposal_nature'] != 'Not specified':
            case_context += f"Outcome: {case_chunks[0]['disposal_nature']}\n"
        case_context += "\n".join([c['text'] for c in case_chunks])
        context_parts.append(case_context)
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Improved prompt - more precise instructions
    prompt = f"""You are a legal research assistant analyzing Indian Supreme Court cases. Answer the user's question based ONLY on the provided excerpts.

STRICT RULES:
1. Use ONLY information from the provided excerpts - no external knowledge
2. For each case, state what the excerpt says the court decided or discussed
3. If the excerpt only shows procedure or part of a judgment, write "the excerpt does not show the holding" instead of guessing
4. Do NOT attribute one judge's opinion to "the court" unless the excerpt says so
5. Mention an article or statute ONLY if it appears in the excerpt
6. Cite by the reference numbers shown (e.g., "[1]", "[2]")
7. Do NOT combine or synthesize reasoning from different cases

ANSWER FORMAT:
[1] Case Name: State what this excerpt says. If it's just procedure, say "the excerpt does not show the holding."

[2] Case Name: State what this excerpt says...

Limits: This answer is based only on the retrieved excerpts, which may be incomplete or dated.

Case Excerpts:
{context}

User Question: {query}

Answer:"""

    print(f"Generating answer using {OLLAMA_MODEL}...")
    
    # Call Ollama with low temperature for more focused responses
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
            "temperature": 0.15  # Low temperature for focused, factual responses
        }
    )
    
    answer = response['message']['content']
    
    return {
        "answer": answer,
        "sources": chunks
    }


if __name__ == "__main__":
    # Test query
    test_query = "What are the rights to a fair trial under human rights law?"
    
    print("=" * 80)
    print("Testing RAG System")
    print("=" * 80)
    
    result = generate(test_query, k=5)
    
    print("\n" + "=" * 80)
    print("QUERY:")
    print("=" * 80)
    print(test_query)
    
    print("\n" + "=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(result["answer"])
    
    print("\n" + "=" * 80)
    print(f"SOURCES ({len(result['sources'])} chunks):")
    print("=" * 80)
    for i, source in enumerate(result["sources"], 1):
        print(f"\n{i}. {source['case_name']} (chunk {source['chunk_number']})")
        print(f"   {source['text'][:150]}...")
