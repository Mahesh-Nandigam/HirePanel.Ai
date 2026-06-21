import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.groq_client import groq_rotator

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

    def evaluate_resume(self, resume_text: str, candidate_name: str) -> dict:
        resume_snippet = " ".join(resume_text.split()[:500])
        prompt = (
            f"You are a Principal Engineer evaluating {candidate_name}'s resume for TECHNICAL DEPTH.\n\n"
            f"Resume:\n{resume_snippet}\n\n"
            f"Perform a deep technical analysis across these dimensions:\n"
            f"1. TECH STACK DEPTH: Which technologies show deep expertise vs superficial listing?\n"
            f"2. ARCHITECTURE: Evidence of system design, microservices, scalable patterns?\n"
            f"3. PRODUCTION READINESS: CI/CD, Docker, cloud deployment, monitoring, testing?\n"
            f"4. AI/ML MATURITY: RAG, LLM integration, fine-tuning, vector DBs, multi-agent systems?\n"
            f"5. PROJECT IMPACT: Quantified achievements (%, $, users)? Or vague descriptions?\n"
            f"6. MISSING SKILLS: What critical engineering skills are absent?\n\n"
            f"Scoring Guide:\n"
            f"- 9-10: Deep expertise across multiple domains, production systems, quantified impact\n"
            f"- 7-8: Good breadth with some depth, real projects, some production experience\n"
            f"- 5-6: Decent fundamentals but limited depth or mostly academic projects\n"
            f"- 3-4: Surface-level skills listing, no real project evidence\n\n"
            f"IMPORTANT: strengths and concerns MUST cite SPECIFIC technologies, projects, or facts from the resume.\n"
            f"chat_message must be a rich, candidate-specific narrative. Never use generic phrases."
        )
        try:
            chat_completion = groq_rotator.execute_completion(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(ResumeEvaluation)}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Resume Agent Error: {e}")
            return {"resume_score": 0.0, "strengths": [], "concerns": [], "chat_message": "Error evaluating resume."}
