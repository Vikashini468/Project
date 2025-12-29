import subprocess

def evaluate_intro_with_llm(intro_text, resume_text, branch, skills):
    prompt = f"""
You are a technical interviewer.

Candidate branch: {branch}
Candidate skills: {', '.join(skills)}

Resume summary:
{resume_text}

Candidate introduction:
{intro_text}

Evaluate the introduction.
Give concise feedback covering:
- Relevance to resume
- Technical clarity
- Missing important points

Do NOT ask questions.
Do NOT greet.
Return ONLY feedback text.
"""

    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    return result.stdout.strip()
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def generate_branch_question(branch: str, skills: list[str], level: str) -> str:
    prompt = f"""
You are a strict technical interviewer.

Candidate branch: {branch}
Candidate skills: {', '.join(skills)}
Difficulty: {level}

Rules:
- Ask ONE technical interview question
- Question MUST match the branch
- Difficulty must be {level}
- No hints
- No explanation
- No answer
- No greeting
- Output ONLY the question text

Ask now.
"""

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    res = requests.post("http://localhost:11434/api/generate", json=payload)
    res.raise_for_status()

    question = res.json()["response"].strip()
    return question.split("\n")[0]

def evaluate_technical_answer(
    question: str,
    answer: str,
    branch: str,
    level: str
) -> str:

    prompt = f"""
You are a technical interviewer.

Branch: {branch}
Difficulty: {level}

Question:
{question}

Candidate answer:
{answer}

Evaluate the answer.
Give concise feedback covering:
- Correctness
- Depth for the given difficulty
- One improvement suggestion

Rules:
- No greeting
- No follow-up questions
- No answer reveal
- Output ONLY feedback text
"""

    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    return result.stdout.strip()
