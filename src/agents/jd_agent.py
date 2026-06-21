import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.groq_client import groq_rotator

load_dotenv()

class JDEvaluation(BaseModel):
    jd_fit_score: float = Field(description="Score out of 10 for JD alignment.")
    strengths: list[str] = Field(description="Matched skills and experience areas.")
    missing_skills: list[str] = Field(description="Required skills not found or weak in resume.")
    risk_area: str = Field(description="Single biggest risk or gap for this candidate.")

class JDExtraction(BaseModel):
    target_title: str = Field(description="Target job title.")
    required_skills: list[str] = Field(description="Mandatory required skills.")
    preferred_skills: list[str] = Field(description="Preferred skills.")
    required_experience: float = Field(description="Required experience in years.")
    domain: str = Field(description="Target industry domain.")

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

class JDAgent:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    def parse_jd(self, job_description: str) -> dict:
        prompt = f"Parse this job description and extract key structured details.\nJD:\n{job_description}"
        try:
            chat_completion = groq_rotator.execute_completion(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(JDExtraction)}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"JD Parser Error: {e}")
            return {"target_title": "Software Engineer", "required_skills": [], "preferred_skills": [], "required_experience": 0.0, "domain": "General"}

    def evaluate_alignment(self, resume_text: str, parsed_jd: dict) -> dict:
        resume_snippet = " ".join(resume_text.split()[:500])
        required = ', '.join(parsed_jd.get('required_skills', []))
        preferred = ', '.join(parsed_jd.get('preferred_skills', []))
        prompt = (
            f"You are a Talent Acquisition Specialist. Compare this candidate's resume against the job requirements.\n\n"
            f"JOB REQUIREMENTS:\n"
            f"- Role: {parsed_jd.get('target_title', 'Software Engineer')}\n"
            f"- Required Skills: {required}\n"
            f"- Preferred Skills: {preferred}\n"
            f"- Experience Required: {parsed_jd.get('required_experience', 0)} years\n"
            f"- Domain: {parsed_jd.get('domain', 'General')}\n\n"
            f"CANDIDATE RESUME:\n{resume_snippet}\n\n"
            f"For each required skill, check if the resume shows evidence of it.\n"
            f"- strengths: List ONLY skills/experience the candidate DEMONSTRABLY has (with evidence from resume)\n"
            f"- missing_skills: List required skills where resume shows NO or WEAK evidence\n"
            f"- risk_area: Identify the single biggest gap or risk (e.g., 'No React experience despite it being required')\n\n"
            f"Scoring Guide:\n"
            f"- 9-10: All required skills present with strong evidence + preferred skills\n"
            f"- 7-8: Most required skills present, minor gaps\n"
            f"- 5-6: Some required skills missing, partial alignment\n"
            f"- 3-4: Major skill gaps, poor alignment\n\n"
            f"Be SPECIFIC. Reference actual skills and projects from the resume."
        )
        try:
            chat_completion = groq_rotator.execute_completion(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(JDEvaluation)}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"JD Agent Error: {e}")
            return {"jd_fit_score": 0.0, "strengths": [], "missing_skills": [], "risk_area": "Evaluation failed"}
