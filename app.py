import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

st.title("Document Q&A")
st.write("Upload a PDF and ask questions about it.")

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def load_pdf(file):
    reader = PdfReader(file)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text.strip():
            pages.append(text.strip())
    return pages

def chunk_pages(pages):
    chunks = []
    for page_text in pages:
        paragraphs = [p.strip() for p in page_text.split("\n\n") if len(p.strip()) > 50]
        chunks.extend(paragraphs)
    return chunks if chunks else [" ".join(pages)]

def build_db(chunks, model):
    embeddings = model.encode(chunks).tolist()
    db = chromadb.Client()
    collection = db.get_or_create_collection("doc")
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection

def ask(question, collection, model):
    q_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=3)
    context = "\n\n".join(results["documents"][0])
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"Answer based only on this document:\n\n{context}\n\nQuestion: {question}"
        }]
    )
    return response.content[0].text

model = load_model()

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with st.spinner("Processing PDF..."):
        pages = load_pdf(uploaded_file)
        chunks = chunk_pages(pages)
        collection = build_db(chunks, model)
    st.success(f"Ready! Loaded {len(chunks)} chunks.")

    question = st.text_input("Ask a question about your document:")
    if question:
        with st.spinner("Thinking..."):
            answer = ask(question, collection, model)
        st.write("**Answer:**", answer)
