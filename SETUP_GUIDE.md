# Team Setup Guide - RAG Legal AI

This guide will help your teammates get the RAG Legal AI application running on their local machines.

## Prerequisites

- Python 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- Git installed ([Download Git](https://git-scm.com/downloads))
- A Google API key for Gemini (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))
- Stable internet connection

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/akshaypandey01/LegalShield.git
cd LegalShield
```

### 2. Create a Virtual Environment

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- LangChain
- ChromaDB
- Google Generative AI
- Gradio
- and other dependencies

### 4. Set Up Your Google API Key

You need a Google API key to use the Gemini model. 

**Option A: Environment Variable (Recommended)**

**On Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY = "your-api-key-here"
```

**On macOS/Linux:**
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Option B: Create a .env file**

Create a file named `.env` in the project root:
```
GOOGLE_API_KEY=your-api-key-here
```

### 5. Run the Application

```bash
python app.py
```

The application will start and you'll see a message like:
```
Running on local URL:  http://127.0.0.1:7860
```

Open your browser and navigate to `http://localhost:7860`

## What's Already Included

✅ **300 Legal Case Files** - All source documents are in the `data/` folder  
✅ **Pre-built Vector Database** - The `chroma_db/` folder contains the indexed documents  
✅ **No Need to Run `ingest.py`** - Database is ready to use!

This means you can skip the ingestion step and start querying immediately after setup.

## Testing the Application

Try these sample queries:
- "What are landmark cases related to privacy rights?"
- "Find cases involving contract disputes"
- "Summarize judgments about constitutional rights"

## Features

- 🔍 **Semantic Search** - Find relevant legal cases using natural language
- 💬 **Conversational Interface** - Multi-turn conversations with context
- 📊 **Citation Extraction** - Automatic identification of legal citations
- 📁 **Export Results** - Save conversations as Markdown or PDF
- 🎯 **Entity Recognition** - Extract legal entities, dates, and case names

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

### Issue: "Google API Key not found"
**Solution:** Verify your GOOGLE_API_KEY environment variable is set correctly

### Issue: "Port 7860 already in use"
**Solution:** Stop any other Gradio applications or change the port in `app.py`:
```python
demo.launch(server_port=7861)  # Use a different port
```

### Issue: Slow responses
**Solution:** This is normal for the first query. Subsequent queries will be faster due to caching.

## Project Structure

```
RAG LEGAL AI/
├── app.py                  # Main Gradio application
├── rag.py                  # RAG implementation & query processing
├── ingest.py              # Data ingestion script (already run)
├── data/                  # 300 legal case text files
├── chroma_db/            # Pre-built vector database
├── requirements.txt      # Python dependencies
└── venv/                 # Virtual environment (you create this)
```

## Need Help?

- Check the [README.md](README.md) for project overview
- See [SAMPLE_QUERIES.md](SAMPLE_QUERIES.md) for query examples
- Review [QUERY_TYPES_GUIDE.md](QUERY_TYPES_GUIDE.md) for different query types
- Look at [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) for feature details

## Updating Your Local Copy

When changes are pushed to the repository:

```bash
git pull origin main
pip install -r requirements.txt  # In case new dependencies were added
```

---

**Happy Coding! 🚀**

If you encounter any issues not covered here, please reach out to the team.
