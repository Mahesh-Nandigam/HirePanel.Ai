import os
import json
import re
import requests
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.groq_client import groq_rotator

load_dotenv()

class LinkedInContext(BaseModel):
    linkedin_score: float = Field(description="Overall career stability score out of 10.0.")
    chat_message: str = Field(description="A dynamic natural-language message sounding like an experienced HR Director.")

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

class LinkedInAgent:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        self.demo_mode = os.environ.get("DEMO_MODE", "").lower() == "true"

    def extract_linkedin_id(self, url: str) -> str:
        if not url or url == "No":
            return ""
        match = re.search(r'linkedin\.com/in/([A-Za-z0-9_-]+)', url, re.IGNORECASE)
        return match.group(1) if match else ""

    def fetch_linkedin_via_scrapingdog(self, linkedin_url: str) -> dict:
        if self.demo_mode:
            return {}
        api_key = os.environ.get("SCRAPINGDOG_API_KEY")
        if not api_key or not linkedin_url or linkedin_url == "No":
            return {}
        linkedin_id = self.extract_linkedin_id(linkedin_url)
        if not linkedin_id:
            return {}
        endpoint = "https://api.scrapingdog.com/profile"
        params = {"api_key": api_key, "type": "profile", "id": linkedin_id}
        try:
            print(f"Fetching LinkedIn profile from Scrapingdog: id={linkedin_id}")
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Scrapingdog failed with status code {response.status_code}")
        except Exception as e:
            print(f"Error querying Scrapingdog: {e}")
        return {}

    def evaluate_profile(self, resume_text: str, candidate_name: str, linkedin_url: str = "No") -> dict:
        profile_data = self.fetch_linkedin_via_scrapingdog(linkedin_url)

        if profile_data and (not isinstance(profile_data, dict) or profile_data.get("success") == False):
            profile_data = {}

        if profile_data:
            print("Successfully retrieved live LinkedIn data via Scrapingdog!")
            clean_profile = {
                "summary": profile_data.get("summary", ""),
                "experiences": profile_data.get("experiences", []),
                "educations": profile_data.get("education", []),
                "skills": profile_data.get("skills", [])
            }
            prompt = (
                f"Evaluate career stability, tenure, and professional trajectory for {candidate_name} using this LinkedIn data:\n\n"
                f"{json.dumps(clean_profile, indent=2)}\n\n"
                f"Analyze career progression, job-hopping vs stability, and growth trajectory."
            )
        else:
            resume_snippet = " ".join(resume_text.split()[:500])
            prompt = (
                f"You are a Senior HR Director. Evaluate the CAREER STABILITY and PROFESSIONAL TRAJECTORY of {candidate_name} based ONLY on their resume.\n\n"
                f"Resume Evidence:\n{resume_snippet}\n\n"
                f"Analyze these specific career signals:\n"
                f"1. JOB TENURE: How long at each role? Look for dates (e.g., '2022-2024'). Short stints (<1 year) = instability.\n"
                f"2. CAREER PROGRESSION: Were there promotions? Did titles improve (Junior→Senior→Lead)?\n"
                f"3. LEADERSHIP: Did they manage teams, mentor others, or lead projects?\n"
                f"4. PROFESSIONAL DEVELOPMENT: Certifications, community involvement, speaking, mentoring?\n"
                f"5. INTERNSHIP QUALITY: If a student, were internships at strong companies?\n"
                f"6. RED FLAGS: Frequent job changes, unexplained gaps, or lateral moves?\n\n"
                f"Scoring Guide:\n"
                f"- 9-10: Long tenures (2+ years), clear promotions, leadership, mentoring programs\n"
                f"- 7-8: Stable career with good progression, some leadership\n"
                f"- 5-6: Short tenures or limited progression, early career\n"
                f"- 3-4: Frequent job hopping, no clear direction, only internships\n\n"
                f"Your chat_message MUST reference SPECIFIC job roles, companies, or tenure patterns from the resume. Never be generic."
            )

        try:
            chat_completion = groq_rotator.execute_completion(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(LinkedInContext)}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"LinkedIn Agent Error: {e}")
            return {"linkedin_score": 0.0, "chat_message": "Error evaluating LinkedIn profile."}
