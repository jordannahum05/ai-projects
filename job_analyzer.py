import anthropic
from dotenv import load_dotenv
import os

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze(job_description, your_background):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""You are a career coach and hiring expert.

Job Description:
{job_description}

Candidate Background:
{your_background}

Give me:
1. Match score (0-100)
2. Top 3 strengths this candidate has for this role
3. Top 3 gaps or missing skills
4. A short cover letter (3 paragraphs)

Format it clearly with headers."""
        }]
    )
    return response.content[0].text

BACKGROUND = """
I am self-taught with focused AI engineering practice over the past few weeks.

Skills: Python, REST APIs, RAG (Retrieval-Augmented Generation), vector databases, embeddings, AI agents with tool use, FastAPI, SQL, prompt engineering, Claude Code.

Built and deployed:
- A live AI API using FastAPI + Claude + SQLite, deployed on Railway
- A Document Q&A system using ChromaDB and semantic search
- An AI agent with autonomous tool calling
- A Job Application Analyzer using Claude
- A Streamlit web app with file upload and real-time AI responses

I use Claude Code daily to build and ship projects. I can demo live working projects and explain how every part works.

GitHub: github.com/jordannahum05/ai-projects
Live API: web-production-eb10d.up.railway.app
"""

print("=" * 50)
print("     Job Application Analyzer")
print("=" * 50)

print("\nPaste job description into job.txt and press Enter to analyze...")
input()

with open("job.txt", "r", encoding="utf-8") as f:
    job_description = f.read()

print("\nAnalyzing...\n")
result = analyze(job_description, BACKGROUND)
print(result)