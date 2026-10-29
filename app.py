"""
Streamlit chat interface for the Legal Research RAG system.
"""

import streamlit as st
from datetime import datetime
from rag import generate, OLLAMA_MODEL, OLLAMA_HOST

# Page configuration
st.set_page_config(
    page_title="Legal Research Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title and description
st.title("⚖️ Legal Research Assistant")
st.markdown("Chat with an AI assistant that retrieves and cites relevant legal cases.")

# Sidebar configuration
st.sidebar.header("Configuration")
st.sidebar.info(f"**Model:** {OLLAMA_MODEL}\n**Dataset:** Indian Supreme Court")

# Top-K configuration in sidebar
k = st.sidebar.number_input("Top K chunks to retrieve", min_value=1, max_value=20, value=5, 
                             help="Number of relevant case chunks to retrieve for legal queries")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("""
This RAG system:
- Retrieves similar past judgments
- Generates answers with citations
- Only uses retrieved case data

**Tips:**
- Ask legal questions for case retrieval
- Greetings and casual messages get conversational responses
""")

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")

# Download conversation button (shown only if there's at least one answer)
has_answers = any(msg["role"] == "assistant" for msg in st.session_state.messages)
if has_answers:
    if st.sidebar.button("📥 Download Conversation"):
        markdown_export = export_conversation_markdown(st.session_state.messages)
        st.sidebar.download_button(
            label="⬇️ Download Markdown",
            data=markdown_export,
            file_name=f"legal_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

st.sidebar.markdown("---")
st.sidebar.caption(f"💬 {len(st.session_state.messages)} messages in history")


def export_conversation_markdown(messages):
    """
    Export conversation to Markdown format.
    
    Args:
        messages: List of chat messages with optional sources
        
    Returns:
        Markdown-formatted string
    """
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
            # Assistant message without preceding user message (shouldn't happen normally)
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


# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display sources if this is an assistant message with sources
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander(f"📚 View {len(message['sources'])} Source Chunks"):
                for i, source in enumerate(message["sources"], 1):
                    # Use display name with reference number
                    case_display = source.get('case_name_display', source['case_name'])
                    ref_num = source.get('ref_number', i)
                    cnr = source.get('cnr', '')
                    outcome = source.get('disposal_nature', '')
                    
                    # Build header with reference number
                    header = f"**[{ref_num}] {case_display}**"
                    
                    # Add outcome only if not "Not specified"
                    if outcome and outcome != 'Not specified':
                        header += f" • Outcome: {outcome}"
                    
                    st.markdown(header)
                    
                    # Show CNR in small text if available
                    if cnr:
                        st.caption(f"CNR: {cnr}")
                    
                    st.text(source["text"])
                    if i < len(message["sources"]):
                        st.markdown("---")


def is_legal_query(text):
    """
    Determine if the input looks like a legal query or just casual conversation.
    Returns True for legal queries, False for greetings/short inputs.
    """
    text = text.strip().lower()
    
    # Very short inputs are likely greetings
    if len(text) < 10:
        return False
    
    # Common greetings and casual phrases
    casual_phrases = [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "how are you", "what's up", "thanks", "thank you", "bye", "goodbye",
        "ok", "okay", "yes", "no", "sure", "what can you do", "what do you do",
        "who are you", "help me"
    ]
    
    if any(text.startswith(phrase) for phrase in casual_phrases):
        return False
    
    # If it contains legal keywords, it's likely a legal query
    legal_keywords = [
        "case", "court", "law", "legal", "judge", "trial", "verdict", "appeal",
        "defendant", "plaintiff", "rights", "conviction", "evidence", "statute",
        "ruling", "lawsuit", "criminal", "civil", "jurisdiction", "precedent"
    ]
    
    if any(keyword in text for keyword in legal_keywords):
        return True
    
    # Questions longer than 15 words are likely substantive queries
    if len(text.split()) > 15:
        return True
    
    # Default to False for short, non-legal-looking text
    return False


def generate_conversational_response(user_message):
    """
    Generate a conversational response for non-legal queries using the LLM.
    No retrieval, just direct LLM response.
    """
    from ollama import Client
    
    # Create a conversational prompt without case retrieval
    prompt = f"""You are a friendly legal research assistant. The user sent you a casual message (not a legal query).

Respond naturally and helpfully. Keep it brief (1-3 sentences).

Guidelines:
- For greetings: Be welcoming and explain you can help with legal research
- For "what can you do": Explain you search court cases and provide citations
- For thanks: Acknowledge warmly
- For goodbyes: Be friendly
- For other casual messages: Respond naturally while steering toward legal assistance

User message: {user_message}

Your response:"""
    
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
            "num_predict": 100,  # Limit tokens for casual responses (shorter = faster + safer)
            "stop": [
                "User message:",
                "Your response:",
                "\nUser:",
                "\nUser message:",
                "Guidelines:",
                "\n\n\n"  # Stop on excessive newlines
            ]
        }
    )
    
    # Extract response and sanitize
    answer = response['message']['content']
    
    # Safety net: strip any leaked instruction blocks or fabricated turns
    sanitized = sanitize_conversational_response(answer)
    
    return sanitized


def sanitize_conversational_response(text):
    """
    Remove leaked instructions or fabricated conversation turns from LLM output.
    """
    # Markers that indicate leaked prompt or fabricated turns
    leak_markers = [
        "User message:",
        "Your response:",
        "\nUser:",
        "Guidelines:",
        "Respond naturally",
        "Keep it brief",
        "For greetings:",
        "For thanks:",
        "casual message"
    ]
    
    # Find the first occurrence of any leak marker
    first_leak_pos = len(text)
    for marker in leak_markers:
        pos = text.find(marker)
        if pos != -1 and pos < first_leak_pos:
            first_leak_pos = pos
    
    # Truncate at the leak point
    if first_leak_pos < len(text):
        text = text[:first_leak_pos]
    
    # Clean up trailing artifacts
    text = text.strip()
    
    # Remove trailing incomplete sentences (ends with "...")
    # But keep complete sentences
    
    return text


# Chat input
if prompt := st.chat_input("Ask a legal question or say hello..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Check if this is a legal query or casual conversation
                if is_legal_query(prompt):
                    # Legal query - use RAG system
                    result = generate(prompt, k=k)
                    response = result["answer"]
                    sources = result.get("sources", [])
                    
                    # Display response
                    st.markdown(response)
                    
                    # Display sources
                    if sources:
                        with st.expander(f"📚 View {len(sources)} Source Chunks"):
                            for i, source in enumerate(sources, 1):
                                # Use display name with reference number
                                case_display = source.get('case_name_display', source['case_name'])
                                ref_num = source.get('ref_number', i)
                                cnr = source.get('cnr', '')
                                outcome = source.get('disposal_nature', '')
                                
                                # Build header with reference number
                                header = f"**[{ref_num}] {case_display}**"
                                
                                # Add outcome only if not "Not specified"
                                if outcome and outcome != 'Not specified':
                                    header += f" • Outcome: {outcome}"
                                
                                st.markdown(header)
                                
                                # Show CNR in small text if available
                                if cnr:
                                    st.caption(f"CNR: {cnr}")
                                
                                st.text(source["text"])
                                if i < len(sources):
                                    st.markdown("---")
                    
                    # Add assistant message with sources to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources
                    })
                    
                else:
                    # Casual conversation - respond using LLM without retrieval
                    response = generate_conversational_response(prompt)
                    st.markdown(response)
                    
                    # Add assistant message without sources to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}\n\nPlease try again or rephrase your question."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Footer
st.markdown("---")
st.caption("Legal Research Assistant • RAG System • Indian Supreme Court Dataset (CC-BY-4.0)")
