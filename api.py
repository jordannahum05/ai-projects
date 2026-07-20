from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
import io
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import anthropic
from dotenv import load_dotenv
import os
import json
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# database setup
engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///chat_history.db"))
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_message = Column(Text)
    ai_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/chat")
def chat(request: ChatRequest):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": request.message}]
    )
    ai_response = response.content[0].text

    session = Session()
    session.add(Message(user_message=request.message, ai_response=ai_response))
    session.commit()
    session.close()

    return {"response": ai_response}

@app.post("/ask-pdf")
async def ask_pdf(file: UploadFile = File(...), question: str = Form(...)):
    contents = await file.read()
    reader = PdfReader(io.BytesIO(contents))
    text = "\n\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    if not text:
        return {"error": "Could not extract text from PDF"}
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"Answer the question based only on the document below. If the answer is not in the document, say so.\n\nDocument:\n{text[:20000]}\n\nQuestion: {question}"
        }]
    )
    return {"answer": response.content[0].text}

def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

import voyageai
voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

def embed(text: str) -> list[float]:
    result = voyage.embed([text], model="voyage-3")
    return result.embeddings[0]

def chunk_text(text: str, size: int = 500) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), size):
        chunks.append(" ".join(words[i:i+size]))
    return chunks

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    reader = PdfReader(io.BytesIO(contents))
    text = "\n\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    if not text:
        return {"error": "Could not extract text from PDF"}
    chunks = chunk_text(text)
    db = get_db()
    cur = db.cursor()
    for chunk in chunks:
        embedding = embed(chunk)
        cur.execute(
            "INSERT INTO documents (content, embedding, filename) VALUES (%s, %s::vector, %s)",
            (chunk, json.dumps(embedding), file.filename)
        )
    db.commit()
    cur.close()
    db.close()
    return {"chunks": len(chunks), "filename": file.filename}

class RAGRequest(BaseModel):
    question: str

@app.post("/rag-ask")
def rag_ask(request: RAGRequest):
    q_embedding = embed(request.question)
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT content, filename FROM match_documents(%s::vector, %s)",
        (json.dumps(q_embedding), 3)
    )
    results = cur.fetchall()
    cur.close()
    db.close()
    if not results:
        return {"answer": "No relevant documents found."}
    context = "\n\n".join(r[0] for r in results)
    source = results[0][1]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"Answer the question based only on the context below.\n\nContext:\n{context}\n\nQuestion: {request.question}"
        }]
    )
    return {"answer": response.content[0].text, "source": source}

@app.get("/history")
def history():
    session = Session()
    messages = session.query(Message).order_by(Message.created_at.desc()).limit(10).all()
    session.close()
    return [{"id": m.id, "user": m.user_message, "response": m.ai_response[:100] + "...", "time": m.created_at} for m in messages]