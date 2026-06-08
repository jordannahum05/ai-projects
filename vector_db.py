import chromadb
from sentence_transformers import SentenceTransformer
import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.create_collection("hr_docs")

chunks = [
    "Employees get 15 days of PTO per year for their first 3 years. After 3 years, employees get 20 days.",
    "PTO must be approved by your manager at least 2 weeks in advance. Unused PTO can be carried over up to 5 days.",
    "Employees get 10 sick days per year. Sick days do not carry over to the next year.",
    "A doctor's note is required for absences longer than 3 days.",
    "Employees can work remotely up to 3 days per week. Must be available during core hours 10am to 3pm.",
    "Primary caregivers get 16 weeks of paid parental leave. Secondary caregivers get 4 weeks.",
]

embeddings = model.encode(chunks).tolist()

collection.add(
    documents=chunks,
    embeddings=embeddings,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

print(f"Stored {len(chunks)} chunks in vector database")

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ask(question):
    q_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=q_embedding, n_results=2)
    relevant_chunks = results["documents"][0]
    
    context = "\n".join(relevant_chunks)
    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"Answer using only this info:\n{context}\n\nQuestion: {question}"
        }]
    )
    return response.content[0].text

print(ask("how many vacation days do I get?"))
print(ask("can I work from home?"))
print(ask("what happens to unused sick days?"))