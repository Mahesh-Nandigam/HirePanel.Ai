import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.llm_client import llm_client

load_dotenv()

class ResumeEvaluation(BaseModel):
    resume_score: float = Field(description="Score out of 10 for technical depth and skills.")
    strengths: list[str] = Field(description="List of specific technical strengths with evidence from resume.")
    concerns: list[str] = Field(description="List of technical concerns, gaps, or weaknesses found.")
    chat_message: str = Field(description="Detailed manager summary referencing specific resume content.")

def get_simple_schema(pydantic_model) -> str:
    schema = pydantic_model.model_json_schema()
    simple = {}
    for key, val in schema.get("properties", {}).items():
        type_str = val.get("type", "string")
        if type_str == "array":
            items_type = val.get("items", {}).get("type", "string")
            type_str = f"array of {items_type}s"
        desc = val.get("description", "")
        simple[key] = f"<{type_str}: {desc}>"
    return json.dumps(simple, indent=2)

class ResumeAgent:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    def evaluate_resume(self, resume_text: str, candidate_name: str, github_data: dict = None, linkedin_data: dict = None) -> dict:
        resume_snippet = " ".join(resume_text.split()[:500])
        
        gh_context = f"\nGitHub Live Data (for cross-verification):\n{json.dumps(github_data, indent=2)}\n" if github_data else ""
        li_context = f"\nLinkedIn Live Data (for cross-verification):\n{json.dumps(linkedin_data, indent=2)}\n" if linkedin_data else ""

        prompt = (
            f"You are a Principal Engineer and Lead Investigator evaluating {candidate_name}'s resume for TECHNICAL DEPTH and TRUTHFULNESS.\n\n"
            f"Resume Claims:\n{resume_snippet}\n"
            f"{gh_context}"
            f"{li_context}"
            f"\nPerform a deep technical analysis and CROSS-VERIFICATION across these dimensions:\n"
            f"1. TECH STACK DEPTH: Which technologies show deep expertise vs superficial listing? Do their GitHub repos confirm this expertise?\n"
            f"2. ARCHITECTURE: Evidence of system design, microservices, scalable patterns?\n"
            f"3. PRODUCTION READINESS: CI/CD, Docker, cloud deployment, monitoring, testing?\n"
            f"4. EXPERIENCE VERIFICATION: Compare the resume claims (tenure, roles) against the LinkedIn data. Are there discrepancies? If they claim 5 years of Python but have 0 Python repos on GitHub, flag it!\n"
            f"5. PROJECT IMPACT: Quantified achievements (%, $, users)? Or vague descriptions?\n"
            f"6. RED FLAGS: What critical engineering skills are absent, or what claims look exaggerated based on the cross-referenced data?\n\n"
            f"Scoring Guide:\n"
            f"- 9-10: Deep expertise verified by open-source work/LinkedIn, production systems, quantified impact\n"
            f"- 7-8: Good breadth with some depth, real projects, minor or no discrepancies\n"
            f"- 5-6: Decent fundamentals but limited depth or mostly academic projects. Some unverified claims.\n"
            f"- 3-4: Surface-level skills listing, no real project evidence, or major discrepancies/exaggerations discovered.\n"
            f"- CORPORATE PENALTY RULE: If the candidate lacks formal professional experience at a real company (e.g., they only list student clubs, internships, 'Class Representative', or personal projects), you MUST cap their score at 5.0 regardless of their technical skills.\n\n"
            f"IMPORTANT: strengths and concerns MUST cite SPECIFIC technologies, projects, or facts from the resume AND explicitly mention if they are confirmed or contradicted by GitHub/LinkedIn.\n"
            f"chat_message must be a rich, candidate-specific narrative discussing their real capability and any discrepancies found."
        )
        for attempt in range(3):
            try:
                chat_completion = llm_client.execute_completion(
                    messages=[
                        {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                        {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(ResumeEvaluation)}
                    ],
                    model=self.model,
                    response_format={"type": "json_object"},
                )
                return json.loads(chat_completion.choices[0].message.content)
            except Exception as e:
                print(f"Resume Agent Error on attempt {attempt+1}: {e}")
                
        return {"resume_score": 0.0, "strengths": [], "concerns": [], "chat_message": "Error evaluating resume after multiple attempts."}
