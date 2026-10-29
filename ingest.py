"""
Ingest legal cases into ChromaDB with embeddings.
Chunks cases and stores them with metadata for retrieval.
"""

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from load_data import load_cases


def is_tail_chunk(text):
    """
    Check if chunk is mostly closing/procedural lines.
    Skip chunks that consist mainly of "Appeal dismissed", "Agent for appellant", etc.
    
    Args:
        text: Chunk text
        
    Returns:
        True if chunk is mostly tail content
    """
    text_lower = text.lower()
    tail_patterns = [
        'appeal dismissed',
        'appeal allowed',
        'petition dismissed',
        'petition allowed',
        'agent for the appellant',
        'agent for the respondent',
        'advocate for',
        'counsel for',
        'solicitor for',
        'amicus curiae',
    ]
    
    # Count how many tail patterns appear
    pattern_count = sum(1 for pattern in tail_patterns if pattern in text_lower)
    
    # If multiple patterns or chunk is very short with one pattern, it's likely tail content
    word_count = len(text.split())
    if pattern_count >= 2:
        return True
    if pattern_count >= 1 and word_count < 80:
        return True
    
    return False


def is_tail_chunk(text):
    """
    Check if chunk is mostly closing/procedural lines.
    Skip chunks that consist mainly of "Appeal dismissed", "Agent for appellant", etc.
    
    Args:
        text: Chunk text
        
    Returns:
        True if chunk is mostly tail content
    """
    text_lower = text.lower()
    tail_patterns = [
        'appeal dismissed',
        'appeal allowed',
        'petition dismissed',
        'petition allowed',
        'agent for the appellant',
        'agent for the respondent',
        'advocate for',
        'counsel for',
        'solicitor for',
        'amicus curiae',
    ]
    
    # Count how many tail patterns appear
    pattern_count = sum(1 for pattern in tail_patterns if pattern in text_lower)
    
    # If multiple patterns or chunk is very short with one pattern, it's likely tail content
    word_count = len(text.split())
    if pattern_count >= 2:
        return True
    if pattern_count >= 1 and word_count < 80:
        return True
    
    return False


def chunk_text(text, chunk_size=300, overlap=50, min_words=120):
    """
    Split text into overlapping chunks by word count.
    Skip chunks under min_words or tail chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words between chunks
        min_words: Minimum words per chunk (default 120)
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        
        # Skip if too short
        chunk_word_count = len(chunk.split())
        if chunk_word_count < min_words:
            continue
        
        # Skip if tail chunk
        if is_tail_chunk(chunk):
            continue
        
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Stop if we've reached the end
        if i + chunk_size >= len(words):
            break
    
    return chunks
    """
    Split text into overlapping chunks by word count.
    
    Args:
        text: Text to chunk
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words between chunks
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Stop if we've reached the end
        if i + chunk_size >= len(words):
            break
    
    return chunks


def ingest_cases(n=300, chunk_size=300, overlap=50):
    """
    Load cases, chunk them, embed, and store in ChromaDB.
    Safe to re-run - clears and rebuilds the collection.
    
    Args:
        n: Number of cases to load
        chunk_size: Words per chunk
        overlap: Overlapping words between chunks
    """
    print("Initializing ChromaDB...")
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete collection if it exists (safe re-run)
    try:
        client.delete_collection(name="legal_cases")
        print("Existing collection deleted.")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name="legal_cases",
        metadata={"description": "Legal case chunks with embeddings"}
    )
    
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"\nLoading {n} cases...")
    cases = load_cases(n)
    
    print(f"\nChunking and embedding cases...")
    all_chunks = []
    all_metadatas = []
    all_ids = []
    chunk_counter = 0
    
    for case_idx, case in enumerate(cases):
        case_name = case["case_name"]
        text = case["text"]
        disposal_nature = case.get("disposal_nature", "Unknown")
        
        # Chunk the case text (skip tiny/tail chunks)
        chunks = chunk_text(text, chunk_size, overlap, min_words=120)
        
        for chunk_idx, chunk in enumerate(chunks):
            chunk_counter += 1
            all_chunks.append(chunk)
            all_metadatas.append({
                "case_name": case_name,
                "chunk_number": chunk_idx,
                "total_chunks": len(chunks),
                "disposal_nature": disposal_nature,
                "cnr": case.get("cnr", "")  # Add CNR metadata
            })
            all_ids.append(f"{case.get('case_id', f'case_{case_idx}')}_chunk_{chunk_idx}")
        
        if (case_idx + 1) % 50 == 0:
            print(f"  Processed {case_idx + 1} cases ({chunk_counter} chunks)...")
    
    print(f"\nTotal chunks created: {len(all_chunks)}")
    print("Generating embeddings and storing in ChromaDB...")
    
    # Embed and add to collection in batches
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch_chunks = all_chunks[i:i + batch_size]
        batch_metadatas = all_metadatas[i:i + batch_size]
        batch_ids = all_ids[i:i + batch_size]
        
        # Generate embeddings
        embeddings = model.encode(batch_chunks).tolist()
        
        # Add to collection
        collection.add(
            documents=batch_chunks,
            embeddings=embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        
        print(f"  Stored {min(i + batch_size, len(all_chunks))}/{len(all_chunks)} chunks...")
    
    print(f"\n✓ Successfully ingested {len(cases)} cases ({len(all_chunks)} chunks) into ChromaDB!")
    print(f"  Database location: ./chroma_db")


if __name__ == "__main__":
    ingest_cases(300)
