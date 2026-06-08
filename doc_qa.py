import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import anthropic
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def load_pdf(path):
    if not os.path.exists(path):
        print(f"Error: File '{path}' not found.")
        sys.exit(1)
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            pages.append(text.strip())
    if not pages:
        print("Error: Could not extract text from this PDF.")
        sys.exit(1)
    return pages

def chunk_pages(pages):
    chunks = []
    for page_text in pages:
        paragraphs = [p.strip() for p in page_text.split("\n\n") if len(p.strip()) > 50]
        chunks.extend(paragraphs)
    return chunks

def build_db(pdf_path):
    print(f"\nLoading: {os.path.basename(pdf_path)}")
    pages = load_pdf(pdf_path)
    chunks = chunk_pages(pages)
    print(f"Found {len(pages)} pages, {len(chunks)} chunks")

    print("Building search index...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, show_progress_bar=False).tolist()

    db = chromadb.Client()
    collection = db.create_collection("doc")
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    print("Ready.\n")
    return collection, model

def ask(question, collection, model, claude):
    q_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=3)
    context = "\n\n".join(results["documents"][0])

    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"You are a document assistant. Answer based only on the document below. If the answer is not in the document, say so clearly.\n\nDocument:\n{context}\n\nQuestion: {question}"
        }]
    )
    return response.content[0].text

def main():
    print("=" * 50)
    print("       Document Q&A — Powered by Claude")
    print("=" * 50)

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("\nPDF file path: ").strip()

    collection, model = build_db(pdf_path)
    claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print("Ask anything about your document. Type 'quit' to exit.\n")
    while True:
        try:
            question = input("You: ").strip()
            if not question:
                continue
            if question.lower() in ("quit", "exit", "q"):
                print("Goodbye.")
                break
            print("\nThinking...\n")
            answer = ask(question, collection, model, claude)
            print(f"Answer: {answer}\n")
            print("-" * 50 + "\n")
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

main()