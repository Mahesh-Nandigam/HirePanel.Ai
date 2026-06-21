import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.groq_client import groq_rotator

load_dotenv()

class DeciderEvaluation(BaseModel):
    final_score: float = Field(description="The final weighted score out of 100.")
    status: str = Field(description="Must be exactly one of: HIRE, WAITLIST, REJECT")
    chat_message: str = Field(description="Executive summary justifying the decision with specific evidence.")

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

class DeciderAgent:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    def make_decision(self, github_score: float, linkedin_score: float, resume_score: float, jd_score: float, tech_lead_argument: str, hr_argument: str) -> dict:
        raw_final = (resume_score * 0.5) + (github_score * 0.2) + (linkedin_score * 0.15) + (jd_score * 0.15)
        final_score_100 = round(raw_final * 10, 1)

        if final_score_100 >= 70: status = "HIRE"
        elif final_score_100 >= 50: status = "WAITLIST"
        else: status = "REJECT"

        prompt = (
            f"You are the LEAD HIRING MANAGER making the final decision.\n\n"
            f"Computed Score: {final_score_100}/100 (Resume:{resume_score}/10 × 50%, GitHub:{github_score}/10 × 20%, LinkedIn:{linkedin_score}/10 × 15%, JD:{jd_score}/10 × 15%)\n"
            f"Decision: {status}\n\n"
            f"Tech Lead's Assessment: {tech_lead_argument}\n"
            f"HR Partner's Assessment: {hr_argument}\n\n"
            f"Write a 2-3 sentence EXECUTIVE SUMMARY that:\n"
            f"1. States the decision ({status}) and score ({final_score_100})\n"
            f"2. References the strongest evidence FOR the candidate\n"
            f"3. Notes the primary concern or risk\n"
            f"4. Acknowledges any disagreement between Tech Lead and HR\n\n"
            f"Be concise, decisive, and specific. This is a final hiring committee verdict."
        )
        try:
            chat_completion = groq_rotator.execute_completion(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(DeciderEvaluation)}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            data = json.loads(chat_completion.choices[0].message.content)
            # Override with computed math score for consistency
            data["final_score"] = final_score_100
            data["status"] = status
            return data
        except Exception as e:
            print(f"Decider Agent Error: {e}")
            return {"final_score": final_score_100, "status": status, "chat_message": f"Score: {final_score_100}/100. Decision: {status}. Fallback verdict — unable to generate detailed justification."}
