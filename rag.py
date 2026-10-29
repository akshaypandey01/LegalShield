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


def retrieve(query, k=5):
    """
    Retrieve top-k most relevant chunks for a query with diversity.
    ALL retrieval must go through this function (for future audit logging).
    
    Retrieves k*2 chunks initially, then keeps at most 2 per case and returns top k.
    
    Args:
        query: Search query
        k: Number of chunks to retrieve (default 5)
        
    Returns:
        List of dicts with keys: text, case_name, chunk_number, disposal_nature, cnr
    """
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="legal_cases")
    
    # Load embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Embed query
    query_embedding = model.encode(query).tolist()
    
    # Query ChromaDB - retrieve k*2 for diversity
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k * 2
    )
    
    # Format results with diversity (max 2 chunks per case)
    retrieved_chunks = []
    case_chunk_counts = {}
    
    if results['documents'] and len(results['documents']) > 0:
        for i in range(len(results['documents'][0])):
            case_name = results['metadatas'][0][i]['case_name']
            
            # Skip if we already have 2 chunks from this case
            if case_chunk_counts.get(case_name, 0) >= 2:
                continue
            
            retrieved_chunks.append({
                "text": results['documents'][0][i],
                "case_name": case_name,
                "chunk_number": results['metadatas'][0][i]['chunk_number'],
                "disposal_nature": results['metadatas'][0][i].get('disposal_nature', 'Unknown'),
                "cnr": results['metadatas'][0][i].get('cnr', '')
            })
            
            case_chunk_counts[case_name] = case_chunk_counts.get(case_name, 0) + 1
            
            # Stop when we have k chunks
            if len(retrieved_chunks) >= k:
                break
    
    return retrieved_chunks


def generate(query, k=5):
    """
    Generate an answer to the query using retrieved chunks and Ollama.
    Uses consistent case names throughout answer and sources.
    
    Args:
        query: User's legal research question
        k: Number of chunks to retrieve (default 5)
        
    Returns:
        Dict with keys: answer, sources (list of retrieved chunks with cleaned names)
    """
    print(f"Retrieving relevant cases for: '{query}'")
    
    # Retrieve relevant chunks with diversity
    chunks = retrieve(query, k=k)
    
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
