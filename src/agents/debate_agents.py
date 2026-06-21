import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.groq_client import groq_rotator

load_dotenv()

class DebateResponse(BaseModel):
    argument: str = Field(description="A strict 2-3 sentence argument based on your persona, citing specific resume evidence.")
    stance: str = Field(description="Must be exactly one of: STRONG HIRE, HIRE, WEAK HIRE, PASS, STRONG PASS")

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

class TechLeadAgent:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    def evaluate(self, resume_score: float, github_score: float, jd_fit_score: float, candidate_name: str = "The candidate", resume_context: str = "") -> dict:
        prompt = (
            f"You are the SENIOR TECH LEAD on a hiring committee. Give a candid, evidence-based 2-3 sentence technical evaluation of {candidate_name}.\n\n"
            f"Assessment Scores:\n"
            f"- Resume Technical Depth: {resume_score}/10\n"
            f"- Code & Engineering Quality: {github_score}/10\n"
            f"- JD Alignment: {jd_fit_score}/10\n\n"
        )
        if resume_context:
            prompt += f"Key Resume Evidence:\n{resume_context}\n\n"
        prompt += (
            f"RULES:\n"
            f"1. Reference SPECIFIC technologies, projects, or skills from the resume evidence\n"
            f"2. If github_score < 7, note the code quality concern\n"
            f"3. If resume_score > 8 but github_score < 6, call out the imbalance\n"
            f"4. Be constructively critical — mention both what impresses you AND what concerns you technically\n"
            f"5. Your stance should reflect the TECHNICAL merits only, not HR factors\n"
            f"6. A score of 0.0 means data was unavailable — note this rather than penalizing\n\n"
            f"Be the voice of engineering quality. If the candidate is strong technically but lacks production experience, say so."
        )
        try:
            chat_completion = groq_rotator.execute_completion(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(DebateResponse)}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Tech Lead Agent Error: {e}")
            return {"argument": "Error connecting to Tech Lead Agent.", "stance": "PASS"}

class HRAgent:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    def evaluate(self, linkedin_score: float, jd_fit_score: float, candidate_name: str = "The candidate", resume_context: str = "") -> dict:
        prompt = (
            f"You are the HR BUSINESS PARTNER on a hiring committee. Give a candid, evidence-based 2-3 sentence evaluation of {candidate_name} focusing on ORGANIZATIONAL FIT, not technical skills.\n\n"
            f"Assessment Scores:\n"
            f"- Career Stability & Professional Profile: {linkedin_score}/10\n"
            f"- JD Alignment: {jd_fit_score}/10\n\n"
        )
        if resume_context:
            prompt += f"Key Resume Evidence:\n{resume_context}\n\n"
        prompt += (
            f"RULES:\n"
            f"1. Reference SPECIFIC career patterns — job tenures, companies, progression, or gaps from the resume\n"
            f"2. If linkedin_score < 7, raise concerns about stability or career direction\n"
            f"3. If linkedin_score > 8 but jd_fit_score < 6, note the organizational fit vs skill mismatch\n"
            f"4. Consider: Would this person stay 2+ years? Do they show growth mindset? Leadership potential?\n"
            f"5. Your stance should reflect ORGANIZATIONAL factors — culture fit, tenure risk, growth trajectory\n"
            f"6. You may DISAGREE with the Tech Lead — a technically strong candidate might be an organizational risk\n\n"
            f"Be the voice of organizational wisdom. If the Tech Lead would hire but you see red flags (short tenures, no leadership, misaligned career goals), say so."
        )
        try:
            chat_completion = groq_rotator.execute_completion(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(DebateResponse)}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"HR Agent Error: {e}")
            return {"argument": "Error connecting to HR Agent.", "stance": "PASS"}
