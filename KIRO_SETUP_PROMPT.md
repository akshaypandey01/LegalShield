# Kiro Setup Prompt for Teammates

If your teammates are using Kiro IDE, they can simply paste this prompt to get everything set up automatically!

---

## 🤖 Copy & Paste This Prompt to Kiro:

```
Hi! I need to set up the RAG Legal AI project on my local machine. Here's what I need help with:

1. Clone the repository: https://github.com/akshaypandey01/LegalShield.git

2. Set up a Python virtual environment and install all dependencies from requirements.txt

3. Check if Ollama is installed on my system. If not, guide me on how to install it.

4. Once Ollama is installed, help me pull the phi3:mini model with: ollama pull phi3:mini

5. Verify that:
   - The data/ folder has 300 legal case files
   - The chroma_db/ folder exists (pre-built vector database)
   - Ollama is running on localhost:11434

6. Run the application with: python app.py

7. Once it's running, open http://localhost:7860 in my browser

Please guide me through any issues that come up. This is a 100% local RAG system - no API keys needed!
```

---

## 🎯 What Kiro Will Do:

Kiro will automatically:
- ✅ Clone the repository to your workspace
- ✅ Create and activate a virtual environment
- ✅ Install all Python dependencies
- ✅ Check for Ollama installation
- ✅ Help you install Ollama if needed
- ✅ Pull the phi3:mini model
- ✅ Verify all files are present
- ✅ Start the application
- ✅ Troubleshoot any issues

## 🚀 Even Faster Setup (One-Line Version):

For experienced users, you can use this shorter prompt:

```
Clone https://github.com/akshaypandey01/LegalShield.git, set up Python venv, install dependencies, verify Ollama is running with phi3:mini model, then start the app with python app.py
```

---

## 💡 Pro Tips:

1. **First Time with Ollama?** Let Kiro guide you through the installation - it will detect your OS and give specific instructions.

2. **Already have Ollama?** Just tell Kiro: "I already have Ollama installed, skip to pulling the phi3:mini model"

3. **Troubleshooting?** If something fails, just tell Kiro what error you're seeing - it can debug and fix issues automatically.

4. **Want to modify the code?** After setup, you can ask Kiro things like:
   - "Add a new query type for finding cases by date range"
   - "Modify the UI to show case statistics"
   - "Add support for exporting to DOCX format"

---

## 📋 System Requirements Check

Before starting, make sure you have:
- [ ] Python 3.8+ installed
- [ ] At least 4GB free RAM (8GB recommended)
- [ ] ~3GB free disk space
- [ ] Internet connection (for initial setup)

Kiro can verify these for you if you ask!

---

## 🆘 If You Get Stuck

Just tell Kiro:
- "The setup failed at step X"
- "I'm getting error: [paste error message]"
- "Ollama isn't responding"
- "The app won't start"

Kiro will diagnose and fix it! 🔧

---

**Happy Coding!** 🚀
