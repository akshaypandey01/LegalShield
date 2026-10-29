"""
Streamlit chat interface for the Legal Research RAG system.
"""

import streamlit as st
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
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


def export_conversation_pdf(messages):
    """
    Export conversation to PDF format.
    
    Args:
        messages: List of chat messages with optional sources
        
    Returns:
        BytesIO buffer containing PDF data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for PDF elements
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1f1f1f',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2c3e50',
        spaceAfter=10,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=11,
        textColor='#34495e',
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#333333',
        spaceAfter=8,
        leading=14
    )
    
    source_style = ParagraphStyle(
        'SourceStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor='#555555',
        leftIndent=20,
        spaceAfter=6,
        leading=12
    )
    
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor='#666666',
        spaceAfter=4
    )
    
    # Title
    story.append(Paragraph("Legal Research Assistant", title_style))
    story.append(Paragraph("Conversation Export", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata
    export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<b>Export Date:</b> {export_time}", meta_style))
    story.append(Paragraph(f"<b>Model:</b> {OLLAMA_MODEL}", meta_style))
    story.append(Paragraph(f"<b>Dataset:</b> Indian Supreme Court Cases (overthelex/indian-court-decisions)", meta_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Process messages into Q&A exchanges
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
                i += 2
            else:
                i += 1
            
            # Add exchange header
            story.append(Paragraph(f"Exchange {exchange_num}", heading_style))
            
            # Add question
            story.append(Paragraph("<b>Question:</b>", subheading_style))
            # Escape HTML special characters
            question_escaped = question.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(question_escaped, normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Add answer
            if answer:
                story.append(Paragraph("<b>Answer:</b>", subheading_style))
                answer_escaped = answer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                # Replace newlines with line breaks for PDF
                answer_escaped = answer_escaped.replace('\n\n', '<br/><br/>').replace('\n', '<br/>')
                story.append(Paragraph(answer_escaped, normal_style))
                story.append(Spacer(1, 0.1*inch))
                
                # Add sources
                if sources:
                    story.append(Paragraph(f"<b>Sources ({len(sources)} excerpts):</b>", subheading_style))
                    
                    for j, source in enumerate(sources, 1):
                        # Use same cleaned case labels as the app
                        case_display = source.get('case_name_display', source['case_name'])
                        ref_num = source.get('ref_number', j)
                        chunk_num = source.get('chunk_number', 'N/A')
                        cnr = source.get('cnr', '')
                        outcome = source.get('disposal_nature', '')
                        
                        # Source header
                        source_header = f"<b>[{ref_num}] {case_display}</b>"
                        if cnr:
                            source_header += f" (CNR: {cnr})"
                        source_header += f" • Chunk {chunk_num}"
                        if outcome and outcome != 'Not specified':
                            source_header += f" • Outcome: {outcome}"
                        
                        story.append(Paragraph(source_header, source_style))
                        
                        # Excerpt (first 300 chars for PDF)
                        excerpt = source["text"][:300]
                        if len(source["text"]) > 300:
                            excerpt += "..."
                        excerpt_escaped = excerpt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f"<i>{excerpt_escaped}</i>", source_style))
                        story.append(Spacer(1, 0.05*inch))
            
            # Separator between exchanges
            story.append(Spacer(1, 0.2*inch))
        else:
            i += 1
    
    # Footer/Disclaimer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("<b>Disclaimer</b>", heading_style))
    disclaimer_text = """<b>AI-generated research aid based only on retrieved excerpts. Not legal advice. 
    Verify all citations against the original judgments.</b><br/><br/>
    This export was generated by the Legal Research Assistant RAG system using:<br/>
    • Local LLM: {}<br/>
    • Vector Database: ChromaDB<br/>
    • Embeddings: sentence-transformers/all-MiniLM-L6-v2<br/>
    • Dataset: Indian Supreme Court Cases (CC-BY-4.0 License)<br/><br/>
    For research and educational purposes only. Always consult qualified legal professionals for legal matters.""".format(OLLAMA_MODEL)
    
    story.append(Paragraph(disclaimer_text, normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


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
    pdf_buffer = export_conversation_pdf(st.session_state.messages)
    st.sidebar.download_button(
        label="📥 Download Conversation (PDF)",
        data=pdf_buffer,
        file_name=f"legal_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        help="Download conversation as a PDF file"
    )

st.sidebar.markdown("---")
st.sidebar.caption(f"💬 {len(st.session_state.messages)} messages in history")


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
