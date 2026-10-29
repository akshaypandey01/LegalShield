"""Test the conversation export functionality"""
import os
os.environ['HF_HOME'] = 'D:\\huggingface_cache'

from datetime import datetime
from rag import generate, OLLAMA_MODEL

# Simulate a conversation with sources
messages = [
    {
        "role": "user",
        "content": "What are the grounds for granting special leave to appeal?"
    },
    {
        "role": "assistant",
        "content": "[1] Ajtnsr Singh v. The (1953): This case discusses the grounds for granting special leave.\n\n[2] K. DUBA.SH v. COMMISSIONER (1950): The court examined procedural requirements.\n\nLimits: This answer is based only on the retrieved excerpts, which may be incomplete or dated.",
        "sources": [
            {
                "case_name": "Ajtnsr Singh v. The State of Punjab (1953)",
                "case_name_display": "Ajtnsr Singh v. The (1953)",
                "ref_number": 1,
                "chunk_number": 5,
                "text": "The Supreme Court held that special leave to appeal should be granted when there is a substantial question of law of general importance, or when there has been a grave miscarriage of justice. The court emphasized that this discretionary power must be exercised judicially and not arbitrarily.",
                "disposal_nature": "Appeal allowed",
                "cnr": "1953_1_428_438_EN"
            },
            {
                "case_name": "K. DUBA.SH v. COMMISSIONER OF INCOME TAX (1950)",
                "case_name_display": "K. DUBA.SH v. COMMISSIONER (1950)",
                "ref_number": 2,
                "chunk_number": 12,
                "text": "In this case, the court examined the procedural requirements for filing special leave petitions. The judgment clarified that mere disagreement with lower court findings is insufficient ground for granting special leave.",
                "disposal_nature": "Petition dismissed",
                "cnr": "1950_1_969_979_EN"
            }
        ]
    },
    {
        "role": "user",
        "content": "Thank you"
    },
    {
        "role": "assistant",
        "content": "You're welcome! Feel free to ask more legal research questions anytime."
    }
]

# Export function (same as in app.py)
def export_conversation_markdown(messages):
    """Export conversation to Markdown format."""
    export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    markdown = f"""# Legal Research Assistant - Conversation Export

**Export Date:** {export_time}  
**Model:** {OLLAMA_MODEL}  
**Dataset:** Indian Supreme Court Cases (overthelex/indian-court-decisions)

---

"""
    
    # Group messages into Q&A exchanges
    i = 0
    exchange_num = 0
    while i < len(messages):
        msg = messages[i]
        
        if msg["role"] == "user":
            exchange_num += 1
            question = msg["content"]
            
            # Look for corresponding assistant answer
            answer = None
            sources = []
            if i + 1 < len(messages) and messages[i + 1]["role"] == "assistant":
                answer = messages[i + 1]["content"]
                sources = messages[i + 1].get("sources", [])
                i += 2  # Skip both user and assistant message
            else:
                i += 1
            
            # Write exchange
            markdown += f"## Exchange {exchange_num}\n\n"
            markdown += f"**Question:**  \n{question}\n\n"
            
            if answer:
                markdown += f"**Answer:**  \n{answer}\n\n"
                
                if sources:
                    markdown += f"**Sources ({len(sources)} excerpts):**\n\n"
                    for j, source in enumerate(sources, 1):
                        # Use same cleaned case labels as the app
                        case_display = source.get('case_name_display', source['case_name'])
                        ref_num = source.get('ref_number', j)
                        chunk_num = source.get('chunk_number', 'N/A')
                        cnr = source.get('cnr', '')
                        outcome = source.get('disposal_nature', '')
                        
                        # Source header
                        markdown += f"**[{ref_num}] {case_display}**"
                        if cnr:
                            markdown += f" (CNR: {cnr})"
                        markdown += f"  \n*Chunk {chunk_num}*"
                        if outcome and outcome != 'Not specified':
                            markdown += f" • Outcome: {outcome}"
                        markdown += "\n\n"
                        
                        # Excerpt (first 400 chars)
                        excerpt = source["text"][:400]
                        if len(source["text"]) > 400:
                            excerpt += "..."
                        markdown += f"> {excerpt}\n\n"
                    
                    markdown += "\n"
            
            markdown += "---\n\n"
        else:
            # Assistant message without preceding user message
            i += 1
    
    # Footer
    markdown += f"""
---

## Disclaimer

**AI-generated research aid based only on retrieved excerpts. Not legal advice. Verify all citations against the original judgments.**

This export was generated by the Legal Research Assistant RAG system using:
- Local LLM: {OLLAMA_MODEL}
- Vector Database: ChromaDB
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- Dataset: Indian Supreme Court Cases (CC-BY-4.0 License)

For research and educational purposes only. Always consult qualified legal professionals for legal matters.
"""
    
    return markdown


# Test the export
print("=" * 80)
print("TESTING CONVERSATION EXPORT")
print("=" * 80)

markdown_export = export_conversation_markdown(messages)

# Save to file
output_file = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(markdown_export)

print(f"\n✓ Export saved to: {output_file}")
print(f"  File size: {len(markdown_export)} characters")
print(f"  Exchanges: 2")
print(f"  Sources: 2 in first exchange")

print("\nFirst 500 characters of export:")
print("-" * 80)
print(markdown_export[:500])
print("...")

print("\n" + "=" * 80)
print("✓ Test complete - open the file to verify formatting")
