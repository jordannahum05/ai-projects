# AI Engineering Projects

A collection of AI-powered applications built with Python, FastAPI, Claude (Anthropic), Docker, and AWS.

**Live API:** [http://3.144.240.181](http://3.144.240.181) | [API Docs](http://3.144.240.181/docs)

---

## API Endpoints

Deployed on AWS EC2 via Docker. Auto-deploys on every push using GitHub Actions.

### `POST /chat`
Chat with Claude.
```bash
curl -X POST http://3.144.240.181/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

### `POST /ask-pdf`
Upload a PDF and ask questions about it (RAG).
```bash
curl -X POST http://3.144.240.181/ask-pdf \
  -F "file=@document.pdf" \
  -F "question=What is this document about?"
```

### `GET /history`
Get the last 10 chat messages from the database.

---

## Other Projects

### Document Q&A (`doc_qa.py`)
Command-line version with ChromaDB vector search and sentence-transformers embeddings.

### Job Application Analyzer (`job_analyzer.py`)
Paste a job description — get a match score, skill gaps, and a tailored cover letter.

### AI Agent (`agent.py`)
Autonomous agent using Claude tool calling to complete multi-step tasks.

---

## Stack

- Python, FastAPI, SQLAlchemy, pypdf
- Anthropic SDK (Claude API)
- Docker
- AWS EC2
- GitHub Actions (CI/CD)

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
```

Run locally:
```bash
uvicorn api:app --reload
```

Run with Docker:
```bash
docker build -t app-review .
docker run -p 8000:8000 --env-file .env app-review
```
