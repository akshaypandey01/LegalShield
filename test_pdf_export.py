"""Test PDF export functionality"""
import os
os.environ['HF_HOME'] = 'D:\\huggingface_cache'

from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from rag import OLLAMA_MODEL

# Simulate a conversation
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
    }
]

def export_conversation_pdf(messages):
    """Export conversation to PDF format."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    story = []
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
    story.append(Paragraph(f"<b>Dataset:</b> Indian Supreme Court Cases", meta_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Process messages
    i = 0
    exchange_num = 0
    while i < len(messages):
        msg = messages[i]
        
        if msg["role"] == "user":
            exchange_num += 1
            question = msg["content"]
            
            answer = None
            sources = []
            if i + 1 < len(messages) and messages[i + 1]["role"] == "assistant":
                answer = messages[i + 1]["content"]
                sources = messages[i + 1].get("sources", [])
                i += 2
            else:
                i += 1
            
            story.append(Paragraph(f"Exchange {exchange_num}", heading_style))
            story.append(Paragraph("<b>Question:</b>", subheading_style))
            question_escaped = question.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(question_escaped, normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            if answer:
                story.append(Paragraph("<b>Answer:</b>", subheading_style))
                answer_escaped = answer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                answer_escaped = answer_escaped.replace('\n\n', '<br/><br/>').replace('\n', '<br/>')
                story.append(Paragraph(answer_escaped, normal_style))
                story.append(Spacer(1, 0.1*inch))
                
                if sources:
                    story.append(Paragraph(f"<b>Sources ({len(sources)} excerpts):</b>", subheading_style))
                    
                    for j, source in enumerate(sources, 1):
                        case_display = source.get('case_name_display', source['case_name'])
                        ref_num = source.get('ref_number', j)
                        chunk_num = source.get('chunk_number', 'N/A')
                        cnr = source.get('cnr', '')
                        outcome = source.get('disposal_nature', '')
                        
                        source_header = f"<b>[{ref_num}] {case_display}</b>"
                        if cnr:
                            source_header += f" (CNR: {cnr})"
                        source_header += f" • Chunk {chunk_num}"
                        if outcome and outcome != 'Not specified':
                            source_header += f" • Outcome: {outcome}"
                        
                        story.append(Paragraph(source_header, source_style))
                        
                        excerpt = source["text"][:300]
                        if len(source["text"]) > 300:
                            excerpt += "..."
                        excerpt_escaped = excerpt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f"<i>{excerpt_escaped}</i>", source_style))
                        story.append(Spacer(1, 0.05*inch))
            
            story.append(Spacer(1, 0.2*inch))
        else:
            i += 1
    
    # Disclaimer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("<b>Disclaimer</b>", heading_style))
    disclaimer_text = f"""<b>AI-generated research aid based only on retrieved excerpts. Not legal advice. 
    Verify all citations against the original judgments.</b><br/><br/>
    This export was generated by the Legal Research Assistant RAG system using:<br/>
    • Local LLM: {OLLAMA_MODEL}<br/>
    • Vector Database: ChromaDB<br/>
    • Embeddings: sentence-transformers/all-MiniLM-L6-v2<br/>
    • Dataset: Indian Supreme Court Cases (CC-BY-4.0 License)<br/><br/>
    For research and educational purposes only. Always consult qualified legal professionals for legal matters."""
    
    story.append(Paragraph(disclaimer_text, normal_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Test
print("=" * 80)
print("TESTING PDF EXPORT")
print("=" * 80)

pdf_buffer = export_conversation_pdf(messages)

# Save to file
output_file = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
with open(output_file, 'wb') as f:
    f.write(pdf_buffer.read())

pdf_size = os.path.getsize(output_file)

print(f"\n✓ PDF saved to: {output_file}")
print(f"  File size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")
print(f"  Exchanges: 1")
print(f"  Sources: 2")

print("\n" + "=" * 80)
print("✓ Test complete - open the PDF to verify formatting")
