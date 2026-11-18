# Query Types Guide

## Quick Reference: What Can Your RAG System Do?

This guide shows all the types of queries your enhanced legal RAG system can handle, organized by capability.

---

## 1. 📝 General Legal Questions

**What it does:** Retrieves relevant case excerpts and generates answers with citations.

**Query patterns:**
- "What are the [legal concept]?"
- "How does the court interpret [statute/article]?"
- "What are the grounds for [legal action]?"
- "What is the test for [legal doctrine]?"

**Examples:**
```
✓ "What are the grounds for granting special leave to appeal?"
✓ "How does the court interpret Article 14?"
✓ "What are the constitutional rights of arrested persons?"
✓ "What is the test for determining res judicata?"
✓ "What are the requirements for proving negligence?"
```

**Use when:** You need general legal information on a topic.

---

## 2. 📄 Case Summarization

**What it does:** Generates comprehensive summaries of specific cases.

**Query patterns:**
- Case ID: "SC_0001", "SC_0025", etc.
- Case name: Full or partial case name
- CNR number: If available in metadata

**Examples:**
```
✓ "SC_0001"
✓ "SC_0142"
✓ "Gopalan v. State of Madras"  (if exact name exists)
```

**Output structure:**
- **Facts**: Parties, events, lower court decisions
- **Legal Issues**: Questions the court addressed
- **Holding**: What the court decided
- **Reasoning**: Why the court decided this way
- **Outcome**: Final disposition

**Use when:** You need a complete overview of a specific case.

---

## 3. 🔍 Find Similar Cases

**What it does:** Discovers cases with similar facts, issues, or reasoning.

**Query patterns:**
- Case ID as input
- Case name as input
- Returns top-K similar cases with relevance scores

**Examples:**
```
✓ "SC_0001"  → Find cases similar to SC_0001
✓ "SC_0075"  → Find cases similar to SC_0075
```

**Output includes:**
- Similar case names
- Outcomes (Appeal allowed/dismissed, etc.)
- Number of matching chunks (relevance proxy)
- Sample excerpts from each case

**Use when:**
- Looking for precedents with similar fact patterns
- Finding cases on the same legal doctrine
- Building citation networks
- Comparative case analysis

---

## 4. 🎯 Outcome-Filtered Queries

**What it does:** Searches only within cases with specific outcomes.

**Available filters:**
- "Appeal allowed"
- "Appeal dismissed"
- "Petition allowed"
- "Petition dismissed"

**Query patterns:**
```
Query: [legal question]
Filter: [outcome type]
```

**Examples:**
```
✓ Query: "grounds for constitutional validity"
   Filter: Appeal allowed
   → Returns only cases where appeals were allowed

✓ Query: "police misconduct"
   Filter: Petition dismissed
   → Returns only cases where petitions were dismissed
```

**Use when:**
- You want to see only successful/unsuccessful appeals
- Studying patterns in granted vs. denied cases
- Understanding what arguments work/don't work

---

## 5. 📚 Full Case Retrieval

**What it does:** Gets all chunks from a specific case (not just top-K).

**Query patterns:**
- Programmatic: `get_case_by_name("SC_0001")`
- Returns all chunks in order

**Examples:**
```python
# In Python
from rag import get_case_by_name

chunks = get_case_by_name("SC_0001")
# Returns all chunks from the case, sorted by chunk_number
```

**Use when:**
- Deep diving into a specific case
- Need complete context beyond summary
- Extracting specific sections

---

## 6. 🔎 Topic-Based Search

**What it does:** Semantic search for cases discussing specific topics.

**Query patterns:**
- Topic or doctrine name
- Legal concepts
- Constitutional provisions

**Examples:**
```
✓ "freedom of speech"
✓ "due process"
✓ "Article 21 life and liberty"
✓ "natural justice principles"
✓ "separation of powers"
```

**Use when:** Exploring cases on a legal topic or doctrine.

---

## 7. 📊 Comparative Queries

**What it does:** Compare multiple cases side by side (programmatic).

**Query patterns:**
```python
# Get summaries of multiple cases
case1 = summarize_case("SC_0001")
case2 = summarize_case("SC_0010")
# Compare outcomes, reasoning, etc.
```

**Examples:**
```python
# Compare constitutional interpretation
case1 = summarize_case("SC_0025")  # Freedom of speech case
case2 = summarize_case("SC_0042")  # Another speech case
# Analyze differences in reasoning
```

**Use when:**
- Comparing how different courts/judges approached similar issues
- Analyzing evolution of legal doctrine
- Identifying conflicting precedents

---

## 8. 💬 Conversational Queries

**What it does:** Handles casual conversation, greetings, thanks.

**Query patterns:**
- Greetings: "Hello", "Hi", "Good morning"
- Thanks: "Thank you", "Thanks"
- Questions: "What can you do?", "Help me"

**Examples:**
```
✓ "Hello"  → Greeting response
✓ "Thank you"  → Acknowledgment
✓ "What can you help with?"  → Capability explanation
```

**Use when:** Non-legal interactions with the system.

---

## 9. 🎭 Multi-hop Reasoning (Planned)

**What it does:** Chain multiple queries together.

**Query patterns (future):**
- "Find cases similar to SC_0042 that were decided after 1960"
- "What precedents did cases about X cite, and what do those say about Y?"

**Currently:** Can be done programmatically by chaining function calls.

---

## Query Selection Flowchart

```
Do you know the case ID/name?
├─ Yes
│  ├─ Want a summary? → Use Summarize Mode (📄)
│  └─ Want similar cases? → Use Find Similar Mode (🔍)
└─ No
   ├─ Have a legal question?
   │  ├─ Care about outcome? → Use Advanced Search with filter (🎯)
   │  └─ General question? → Use Chat Mode (💬)
   └─ Casual conversation? → Use Chat Mode (💬)
```

---

## Best Practices

### 1. **Start Broad, Then Narrow**
```
Step 1: "What are grounds for appeal?" (Chat Mode)
Step 2: Filter by "Appeal allowed" (Advanced Search)
Step 3: Find similar to best case (Find Similar)
Step 4: Summarize that case (Summarize Mode)
```

### 2. **Verify Critical Information**
- Summaries are AI-generated from excerpts
- Always check original judgments for court submissions
- Cross-reference multiple cases

### 3. **Use Metadata Wisely**
- Outcome filters help find precedents
- CNR numbers are unique identifiers
- Chunk counts indicate coverage

### 4. **Combine Modes**
- Chat for exploration
- Summarize for understanding
- Similar for precedents
- Advanced for precision

---

## Query Type Summary Table

| Query Type | Mode | Input | Output | Use Case |
|-----------|------|-------|--------|----------|
| General Q&A | 💬 Chat | Legal question | Answer + sources | Exploring topics |
| Summarize | 📄 Summarize | Case ID/name | Structured summary | Understanding case |
| Similar | 🔍 Find Similar | Case ID/name | Related cases | Finding precedents |
| Filtered | 🎯 Advanced | Question + filter | Targeted results | Specific outcomes |
| Full Case | 📚 API | Case ID/name | All chunks | Deep analysis |
| Topic | 💬 Chat | Topic/doctrine | Relevant cases | Topic research |
| Compare | 📊 Code | Multiple IDs | Multiple summaries | Case comparison |

---

## Advanced Query Patterns

### Pattern 1: Research Pipeline
```
1. Chat: "What are employment discrimination standards?"
2. Note case IDs from sources (e.g., SC_0142)
3. Summarize: "SC_0142"
4. Find Similar: "SC_0142"
5. Filter: "Appeal allowed" + "discrimination"
```

### Pattern 2: Precedent Discovery
```
1. Find Similar to known good case
2. Filter similar cases by outcome
3. Summarize top matches
4. Compare reasoning across cases
```

### Pattern 3: Outcome Analysis
```
1. Query topic with "Appeal allowed" filter
2. Query same topic with "Appeal dismissed" filter
3. Compare what arguments succeed vs. fail
```

---

## Limitations

**Current system cannot:**
- ❌ Query by date ranges (all cases 1950-1966)
- ❌ Filter by judge names
- ❌ Search by party names
- ❌ Track citation networks automatically
- ❌ Extract specific statutes/articles mentioned
- ❌ Multi-hop reasoning in UI (code only)

**Future enhancements planned for these capabilities.**

---

## Examples by Legal Domain

### Constitutional Law
```
✓ "What is the scope of Article 14 equality?"
✓ "How is Article 21 right to life interpreted?"
✓ "What are limits on freedom of speech under Article 19?"
```

### Criminal Law
```
✓ "What are grounds for bail?"
✓ "What is the test for criminal intent?"
✓ "What are rights during police custody?"
```

### Civil Procedure
```
✓ "What is the res judicata doctrine?"
✓ "When can appeals be filed?"
✓ "What are requirements for jurisdiction?"
```

### Administrative Law
```
✓ "What is natural justice?"
✓ "When can administrative decisions be challenged?"
✓ "What is judicial review scope?"
```

---

## Getting Help

If you're unsure which query type to use:
1. Start with **Chat Mode** for exploration
2. Use **Summarize** when you find interesting case IDs
3. Use **Find Similar** to discover related cases
4. Use **Advanced Search** when you know what outcome you want

**Remember:** All modes complement each other - use them together for comprehensive research!
