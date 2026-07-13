from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import anthropic
from dotenv import load_dotenv
import os

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
engine = create_engine("sqlite:///chat_history.db")
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

@app.get("/history")
def history():
    session = Session()
    messages = session.query(Message).order_by(Message.created_at.desc()).limit(10).all()
    session.close()
    return [{"id": m.id, "user": m.user_message, "response": m.ai_response[:100] + "...", "time": m.created_at} for m in messages]