# LegalShield - Legal Research RAG System

A production-ready Retrieval-Augmented Generation (RAG) system for legal research using Indian Supreme Court cases. Built with local LLMs (Ollama), ChromaDB vector storage, and an intuitive Streamlit chat interface.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-CC--BY--4.0-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

## ✨ Features

- 📚 **300 Indian Supreme Court cases** (1950-1966) with quality filtering
- 🔍 **Smart retrieval** with diversity filtering (max 2 chunks per case)
- 🤖 **Local LLM** using Ollama (phi3:mini) - no cloud dependencies
- 💾 **ChromaDB vector database** with 7,109 high-quality chunks
- 🎯 **Clean case names** extracted from OCR text with "X v. Y" format
- 💬 **Conversational interface** - handles both legal queries and casual chat
- 📝 **Precise citations** with consistent [1], [2] reference numbering
- 🔬 **Quality controls**: Min 120 words per chunk, tail chunk filtering
- 🌐 **Streamlit web UI** with message history and source viewing

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama** (for local LLM):
   - Download from [ollama.ai](https://ollama.ai)
   - Pull the model: `ollama pull phi3:mini`

2. **Python 3.8+** installed

### Installation

```powershell
# Clone the repository
git clone https://github.com/akshaypandey01/LegalShield.git
cd LegalShield

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Data Setup

```powershell
# Set Hugging Face cache location (optional, if C: drive is limited)
$env:HF_HOME = "D:\huggingface_cache"

# Load 300 cases from Hugging Face (saves to ./data/)
python load_data.py

# Chunk, embed, and store in ChromaDB (~10 minutes on CPU)
python ingest.py
```

### Run the App

```powershell
# Launch Streamlit interface
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## 📊 System Architecture

```
User Query → Streamlit UI
              ↓
         Query Classifier (Legal vs Casual)
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
Legal Query        Casual Chat
    ↓                   ↓
Embedding          Direct LLM
    ↓
ChromaDB Retrieval (Top-10)
    ↓
Diversity Filter (Max 2/case)
    ↓
Top-5 Chunks Selected
    ↓
Structured Prompt + LLM (phi3:mini)
    ↓
Answer with [1], [2] Citations
    ↓
Display with Sources
```

## 🎯 Usage Examples

### Legal Queries

```
Q: What are the grounds for granting special leave to appeal?
→ Retrieves relevant cases, generates answer with citations

Q: What are the constitutional rights of arrested persons?
→ Searches cases about arrest procedures and rights

Q: How does the court interpret Article 14 equality?
→ Finds cases discussing constitutional equality
```

### Casual Chat

```
Q: Hello
→ "Hello! I'm your legal research assistant..."

Q: Thank you
→ "You're welcome! Feel free to ask..."
```

## 🔧 Configuration

### `rag.py` Configuration

```python
OLLAMA_HOST = "http://localhost:11434"  # Ollama server
OLLAMA_MODEL = "phi3:mini"               # LLM model
k = 5                                     # Top-K chunks to retrieve
temperature = 0.15                        # Low temp for factual answers
```

### `ingest.py` Configuration

```python
chunk_size = 300        # Words per chunk
overlap = 50            # Overlapping words
min_words = 120         # Minimum chunk size
```

### `load_data.py` Configuration

```python
n = 300                 # Number of cases to load
text_length >= 5000     # Minimum case length
threshold = 0.9         # 90% ASCII (English filter)
year >= 1980 preferred  # But allows older cases
```

## 📁 Project Structure

```
LegalShield/
├── app.py                    # Streamlit chat interface
├── rag.py                    # Retrieval & generation logic
├── load_data.py             # Dataset loading from HuggingFace
├── ingest.py                # Chunking & embedding pipeline
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── SETUP_COMPLETE.md       # Installation notes
├── .gitignore              # Git exclusions
│
├── data/                   # 300 case text files (SC_0001.txt - SC_0300.txt)
│   └── SC_*.txt           # NOT in git (too large)
│
├── chroma_db/             # ChromaDB vector database
│   └── ...                # NOT in git (generated locally)
│
└── venv/                  # Python virtual environment
    └── ...                # NOT in git
```

## 🧪 Testing

```powershell
# Test case name extraction (10 samples)
python test_case_names.py

# Test RAG retrieval and generation
python test_query.py

# Test conversational responses (48 tests)
python test_conversational.py

# Test quality improvements
python test_improvements.py
```

## 📈 Quality Improvements

### Version 2.0 Enhancements

1. **Clean Case Names**: Extracts "X v. Y" from OCR text, strips headers
2. **Chunk Quality**: Min 120 words, filters tail chunks (agents, outcomes)
3. **Better Sampling**: Shuffle buffer for year diversity (not just 1950s)
4. **Improved Prompts**: Explicit instructions about holdings vs procedures
5. **Diversity Filtering**: Max 2 chunks per case in results
6. **Consistent Citations**: Same [1], [2] numbering in answer and sources

### Results

- **Chunks**: 8,801 → 7,109 (19% reduction, higher quality)
- **Year Range**: 1950-1966 (was 1950-1956)
- **Answer Quality**: More precise, less hallucination
- **Case Distribution**: 1959-1961 majority (217/300 cases)

## 🛠️ Technical Stack

- **LLM**: Ollama phi3:mini (local, 3.8B parameters)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384 dim)
- **Vector DB**: ChromaDB (persistent storage)
- **Dataset**: overthelex/indian-court-decisions (Hugging Face)
- **UI**: Streamlit
- **Language**: Python 3.12

## 📊 Database Stats

- **Cases**: 300 Indian Supreme Court judgments
- **Chunks**: 7,109 text chunks (120-300 words each)
- **Embeddings**: 384-dimensional vectors
- **Storage**: 63.7 MB ChromaDB
- **Years**: 1950-1966 with diversity
- **License**: CC-BY-4.0

## 🔒 Data Privacy

- **100% Local**: All data and models run on your machine
- **No Cloud APIs**: Ollama runs locally (no OpenAI/Anthropic calls)
- **Offline Ready**: Works without internet after setup
- **Data Location**: D: drive for Ollama models, project folder for data

## 🐛 Troubleshooting

### ChromaDB locked error
```powershell
# Stop Python processes
Stop-Process -Name python -Force
# Delete and re-ingest
Remove-Item -Path "chroma_db" -Recurse -Force
python ingest.py
```

### Ollama not responding
```powershell
# Check Ollama status
ollama list
# Restart Ollama service (Windows)
# Or run: ollama serve
```

### Slow generation
- Reduce chunk count (k=3 instead of k=5)
- Use faster model: `ollama pull phi3:mini`
- Ensure Ollama is using GPU if available

### Empty results
- Check ChromaDB exists: `Test-Path chroma_db`
- Re-run ingestion if database is missing
- Verify Ollama is running: `ollama list`

## 📄 License

- **Code**: MIT License (your implementation)
- **Dataset**: CC-BY-4.0 (overthelex/indian-court-decisions)
- **Models**: Respective licenses (phi3:mini, all-MiniLM-L6-v2)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Contact

- **GitHub**: [@akshaypandey01](https://github.com/akshaypandey01)
- **Repository**: [LegalShield](https://github.com/akshaypandey01/LegalShield)

## 🙏 Acknowledgments

- Indian Supreme Court for public case data
- Hugging Face for dataset hosting
- Ollama for local LLM inference
- ChromaDB for vector storage
- Streamlit for UI framework

---

**Note**: This system is for research and educational purposes. Always verify legal information with qualified professionals.
