import subprocess
import json
import re
def extract_skills_and_branch(resume_text: str) -> dict:
    prompt = f"""
You are an AI interviewer.

From the resume text below:
1. Identify the engineering branch (CSE, ECE, EEE, Civil, Mech, AI/DS, AIML, etc.)
2. Extract only technical skills (no soft skills)

Return STRICT JSON only in this format:
{{
  "branch": "...",
  "skills": ["skill1", "skill2", "skill3"]
}}

Resume:
{resume_text}
"""

    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    # Ollama sometimes adds text before JSON → clean it
    output = result.stdout.strip()
    match = re.search(r"\{[\s\S]*\}", output)
    if not match:
     raise ValueError("No JSON found in LLM output")

    json_text = match.group(0)
    return json.loads(json_text)
