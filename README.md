# AI Engineering Projects

A collection of AI-powered applications built with Python, Claude (Anthropic), and modern LLM tooling.

**Live API:** [https://web-production-eb10d.up.railway.app](https://web-production-eb10d.up.railway.app) | [API Docs](https://web-production-eb10d.up.railway.app/docs)

---

## Projects

### 1. Document Q&A (`doc_qa.py`)
Upload any PDF and ask questions about it in natural language.

- Reads and chunks PDF documents
- Creates semantic embeddings using `sentence-transformers`
- Stores and searches chunks in ChromaDB (vector database)
- Answers questions using Claude — grounded in the document, no hallucination

**Run it:**
```bash
python doc_qa.py
```

---

### 2. Job Application Analyzer (`job_analyzer.py`)
Paste a job description and your background — get a match score, skill gaps, and a cover letter.

- Analyzes fit between candidate and role
- Identifies top strengths and missing skills
- Generates a tailored cover letter using Claude

**Run it:**
```bash
python job_analyzer.py
```

---

### 3. AI Agent (`agent.py`)
An autonomous agent that uses tool calling to complete multi-step tasks.

- Claude decides which tools to call and in what order
- Searches for jobs and retrieves details without being told how
- Demonstrates the full agent loop: reason → call tool → observe → continue

**Run it:**
```bash
python agent.py
```

---

## Stack

- Python
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) (Claude API)
- ChromaDB
- sentence-transformers
- pypdf

## Setup

```bash
pip install anthropic chromadb sentence-transformers pypdf python-dotenv fpdf2
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
```
