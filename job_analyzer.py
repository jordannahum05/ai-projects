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

print("=" * 50)
print("     Job Application Analyzer")
print("=" * 50)

print("\nPaste the job description (press Enter twice when done):")
lines = []
while True:
    line = input()
    if line == "" and lines and lines[-1] == "":
        break
    lines.append(line)
job_description = "\n".join(lines[:-1])

print("\nDescribe your background and skills (press Enter twice when done):")
lines = []
while True:
    line = input()
    if line == "" and lines and lines[-1] == "":
        break
    lines.append(line)
background = "\n".join(lines[:-1])

print("\nAnalyzing...\n")
result = analyze(job_description, background)
print(result)