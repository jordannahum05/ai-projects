import anthropic
from dotenv import load_dotenv
import os

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# tools are things claude can "call"
tools = [
    {
        "name": "search_jobs",
        "description": "Search for job listings by keyword",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "job title or skill to search for"}
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "get_job_details",
        "description": "Get full details of a specific job by id",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string"}
            },
            "required": ["job_id"]
        }
    }
]

# fake job data (in real life this would hit an API)
def search_jobs(keyword):
    return [
        {"id": "1", "title": "AI Engineer", "company": "OpenAI", "location": "Remote"},
        {"id": "2", "title": "ML Engineer", "company": "Google", "location": "NYC"},
    ]

def get_job_details(job_id):
    details = {
        "1": {"title": "AI Engineer", "company": "OpenAI", "salary": "$180k", "requirements": "Python, LLMs, RAG"},
        "2": {"title": "ML Engineer", "company": "Google", "salary": "$200k", "requirements": "Python, TensorFlow, distributed systems"},
    }
    return details.get(job_id, {"error": "not found"})

# run the tool claude asked for
def run_tool(name, inputs):
    if name == "search_jobs":
        return search_jobs(inputs["keyword"])
    if name == "get_job_details":
        return get_job_details(inputs["job_id"])

# agent loop
messages = [{"role": "user", "content": "Find me AI engineering jobs and tell me which one pays more"}]

while True:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        tools=tools,
        messages=messages
    )

    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "end_turn":
        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)
        break

    # collect ALL tool results before continuing
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"Claude is calling: {block.name}({block.input})")
            result = run_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result)
            })

    if tool_results:
        messages.append({"role": "user", "content": tool_results})