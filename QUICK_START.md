# Quick Start Guide - RAG Legal AI

Get the Legal Research Assistant running on your laptop in **5 minutes**!

## What You Need

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Ollama** - [Download](https://ollama.com/download) (Local AI engine - FREE!)
3. **Git** - [Download](https://git-scm.com/downloads)

## Setup (5 Steps)

### 1️⃣ Clone & Navigate
```bash
git clone https://github.com/akshaypandey01/LegalShield.git
cd LegalShield
```

### 2️⃣ Create Virtual Environment
**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Ollama (One-time)
```bash
# Install Ollama from https://ollama.com/download
# Then pull the AI model:
ollama pull phi3:mini
```

### 5️⃣ Run the App!
```bash
python app.py
```

Open your browser: **http://localhost:7860**

## ✅ What's Included

- ✅ **300 Legal Cases** already loaded
- ✅ **Vector Database** pre-built and ready
- ✅ **100% Local** - No cloud, no API keys, no costs
- ✅ **Private** - Your data never leaves your machine

## 🎯 Try These Queries

- "What are landmark cases related to privacy rights?"
- "Find cases about contract disputes"
- "Summarize SC_0001"
- "Find similar cases to SC_0050"

## 💡 Key Features

| Feature | Description |
|---------|-------------|
| 💬 Chat Mode | Ask legal questions naturally |
| 📄 Summarize | Get case summaries by ID |
| 🔍 Find Similar | Discover related cases |
| 📥 Export | Download as PDF/Markdown |
| 🎯 Filter | Search by case outcome |

## ⚠️ Common Issues

**"Cannot connect to Ollama"**
- Make sure Ollama is installed and running
- Run: `ollama list` to check

**"Model not found"**
- Run: `ollama pull phi3:mini`

**Slow first query?**
- Normal! Ollama loads model into memory (~30 seconds)
- Subsequent queries are much faster

## 🔧 System Requirements

- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** ~3GB for model + database
- **OS:** Windows, macOS, or Linux
- **Internet:** Only needed for initial setup

## 📚 Full Documentation

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [README.md](README.md) - Project overview
- [SAMPLE_QUERIES.md](SAMPLE_QUERIES.md) - Example queries
- [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) - All features explained

## 🚀 Next Steps

1. Start with simple queries to test the system
2. Try different query modes (Chat, Summarize, Find Similar)
3. Experiment with outcome filters
4. Export your research as PDF

---

**Need Help?** Check the troubleshooting section in [SETUP_GUIDE.md](SETUP_GUIDE.md)

**100% Free • 100% Local • 100% Private** 🔒
