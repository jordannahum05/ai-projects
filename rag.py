hr_policy = """
ACME Company HR Policies

PTO Policy:
Employees get 15 days of PTO per year for their first 3 years.
After 3 years, employees get 20 days of PTO per year.
PTO must be approved by your manager at least 2 weeks in advance.
Unused PTO can be carried over up to 5 days to the next year.

Sick Leave:
Employees get 10 sick days per year.
Sick days do not carry over to the next year.
A doctor's note is required for absences longer than 3 days.

Remote Work:
Employees can work remotely up to 3 days per week.
Remote work must be approved by your manager.
Employees must be available during core hours 10am to 3pm.

Parental Leave:
Primary caregivers get 16 weeks of paid parental leave.
Secondary caregivers get 4 weeks of paid parental leave.
Parental leave must be taken within 12 months of the child's birth.
"""
from dotenv import load_dotenv
import os
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ask_document(document, question):
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Use only the document below to answer the question.
If the answer is not in the document, say "I don't know."

DOCUMENT:
{document}

QUESTION:
{question}
"""
            }]
        )
        return message.content[0].text
    except Exception as e:
        return "API error, try again"
print("Ask anything about ACME HR policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")
    if question == "quit":
        break
    answer = ask_document(hr_policy, question)
    print(f"Assistant: {answer}\n")