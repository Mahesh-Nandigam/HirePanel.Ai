import os

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. Intake Agent
intake = """
import os
import json
import re
from pypdf import PdfReader
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class CandidateNameContext(BaseModel):
    candidate_name: str = Field(description="The full name of the candidate extracted from the resume. If not found, output 'Unknown'.")

class IntakeAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model = "llama-3.1-8b-instant"
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\\n"
            return text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""

    def _extract_urls_via_regex(self, text: str):
        github_pattern = r'(?:https?://)?(?:www\\.)?github\\.com/[A-Za-z0-9_-]+'
        linkedin_pattern = r'(?:https?://)?(?:www\\.)?linkedin\\.com/in/[A-Za-z0-9_-]+'
        
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        
        github_url = github_match.group(0) if github_match else "No"
        linkedin_url = linkedin_match.group(0) if linkedin_match else "No"
        
        if github_url != "No" and not github_url.startswith("http"): github_url = "https://" + github_url
        if linkedin_url != "No" and not linkedin_url.startswith("http"): linkedin_url = "https://" + linkedin_url
            
        return github_url, linkedin_url

    def _extract_name_via_llm(self, text: str) -> str:
        if not text.strip(): return "Unknown"
        prompt = f"Extract the candidate's full name from the following resume text. If you cannot find a name, output 'Unknown'. Resume Text:\\n\\n{text}"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps(CandidateNameContext.model_json_schema())}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            data = json.loads(chat_completion.choices[0].message.content)
            return data.get("candidate_name", "Unknown")
        except Exception as e:
            print(f"Error extracting name via LLM: {e}")
            return "Unknown"

    def parse_resume(self, pdf_path: str) -> dict:
        resume_filename = os.path.basename(pdf_path)
        resume_text = self.extract_text_from_pdf(pdf_path)
        if not resume_text.strip(): return {"candidate_name": "Unknown", "github_url": "No", "linkedin_url": "No", "resume_filename": resume_filename}
        github_url, linkedin_url = self._extract_urls_via_regex(resume_text)
        candidate_name = self._extract_name_via_llm(resume_text)
        return {"candidate_name": candidate_name, "github_url": github_url, "linkedin_url": linkedin_url, "resume_filename": resume_filename}
"""
write_file("src/agents/intake_agent.py", intake)

# 2. GitHub Agent
github = """
import os
import json
import requests
import re
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GitHubContext(BaseModel):
    github_score: float = Field(description="Overall technical score out of 10.0.")
    consistency_score: int = Field(description="Score out of 10 based on commit frequency and activity.")
    project_quality_score: int = Field(description="Score out of 10 based on repository stars, forks, and complexity.")
    activity_score: int = Field(description="Score out of 10 based on recent GitHub events.")
    top_languages: List[str] = Field(description="List of primary programming languages used.")
    strengths: List[str] = Field(description="List of candidate's technical strengths.")
    concerns: List[str] = Field(description="List of concerns or red flags.")
    github_summary: str = Field(description="A concise 2-sentence summary of their open-source presence.")
    chat_message: str = Field(description="A dynamic natural-language message sounding like a Senior Engineering Manager.")

class GitHubAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model = "llama-3.1-8b-instant"
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token: self.headers["Authorization"] = f"token {self.github_token}"

    def extract_username(self, github_url: str) -> str:
        if github_url.lower() == "no": return ""
        match = re.search(r'github\\.com/([A-Za-z0-9_-]+)', github_url, re.IGNORECASE)
        return match.group(1) if match else ""

    def fetch_github_data(self, username: str) -> dict:
        if not username: return {}
        base_url = f"https://api.github.com/users/{username}"
        data = {}
        try:
            prof_resp = requests.get(base_url, headers=self.headers)
            if prof_resp.status_code == 200:
                prof = prof_resp.json()
                data['profile'] = {"followers": prof.get("followers", 0), "public_repos": prof.get("public_repos", 0), "bio": prof.get("bio", ""), "created_at": prof.get("created_at", "")}
            repos_resp = requests.get(f"{base_url}/repos?sort=updated&per_page=30", headers=self.headers)
            if repos_resp.status_code == 200:
                data['repositories'] = [{"name": r.get("name"), "stars": r.get("stargazers_count", 0), "fork": r.get("fork", False), "language": r.get("language")} for r in repos_resp.json()]
            events_resp = requests.get(f"{base_url}/events?per_page=30", headers=self.headers)
            if events_resp.status_code == 200:
                events = events_resp.json()
                data['recent_activity'] = {"total_recent_events": len(events), "recent_pushes": len([e for e in events if e.get("type") == "PushEvent"])}
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")
        return data

    def evaluate_profile(self, github_url: str) -> dict:
        username = self.extract_username(github_url)
        empty_resp = {"github_score": 0.0, "chat_message": "No valid GitHub profile provided."}
        if not username: return empty_resp
        api_data = self.fetch_github_data(username)
        if not api_data or 'profile' not in api_data: return empty_resp

        prompt = f"Evaluate this candidate mathematically and qualitatively.\\nRaw GitHub Data:\\n{json.dumps(api_data, indent=2)}\\nProvide score out of 10."
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps(GitHubContext.model_json_schema())}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"GitHub Agent Error: {e}")
            return empty_resp
"""
write_file("src/agents/github_agent.py", github)

# 3. LinkedIn Agent
linkedin = """
import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class LinkedInContext(BaseModel):
    linkedin_score: float = Field(description="Overall career stability score out of 10.0.")
    chat_message: str = Field(description="A dynamic natural-language message.")

class LinkedInAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model = "llama-3.1-8b-instant"

    def evaluate_profile(self, resume_text: str, candidate_name: str) -> dict:
        prompt = f"Evaluate the career stability and tenure length from this text for {candidate_name}.\\nText:\\n{resume_text}"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps(LinkedInContext.model_json_schema())}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            return {"linkedin_score": 0.0, "chat_message": "Error evaluating LinkedIn profile."}
"""
write_file("src/agents/linkedin_agent.py", linkedin)

# 4. Resume Agent
resume = """
import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class ResumeEvaluation(BaseModel):
    resume_score: float = Field(description="Score out of 10 for technical depth and skills.")
    strengths: list[str] = Field(description="List of key strengths.")
    chat_message: str = Field(description="Manager summary.")

class ResumeAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model = "llama-3.1-8b-instant"

    def evaluate_resume(self, resume_text: str, candidate_name: str) -> dict:
        prompt = f"Evaluate the technical depth of this resume for {candidate_name}.\\nResume:\\n{resume_text}"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps(ResumeEvaluation.model_json_schema())}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            return {"resume_score": 0.0, "strengths": [], "chat_message": "Error evaluating resume."}
"""
write_file("src/agents/resume_agent.py", resume)

# 5. JD Agent
jd = """
import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class JDEvaluation(BaseModel):
    jd_fit_score: float = Field(description="Score out of 10.")
    strengths: list[str] = Field(description="List of matches.")

class JDAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model = "llama-3.1-8b-instant"

    def evaluate_alignment(self, resume_text: str, job_description: str, resume_score: float, github_score: float, linkedin_score: float) -> dict:
        prompt = f"Evaluate the resume against this JD.\\nJD:\\n{job_description}\\nResume:\\n{resume_text}"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps(JDEvaluation.model_json_schema())}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            data = json.loads(chat_completion.choices[0].message.content)
            jd_fit_score = data.get("jd_fit_score", 0.0)
            data["final_alignment_score"] = round(((resume_score * 0.5) + (github_score * 0.2) + (linkedin_score * 0.15) + (jd_fit_score * 0.15)) * 10, 1)
            return data
        except Exception as e:
            return {"jd_fit_score": 0.0, "final_alignment_score": 0.0, "strengths": []}
"""
write_file("src/agents/jd_agent.py", jd)

# 6. Debate Agents
debate = """
import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class DebateResponse(BaseModel):
    argument: str = Field(description="A strict 2-3 sentence argument based on your persona.")
    stance: str = Field(description="Must be exactly one of: STRONG HIRE, HIRE, WEAK HIRE, PASS, STRONG PASS")

class TechLeadAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model = "llama-3.1-8b-instant"

    def evaluate(self, resume_score: float, github_score: float, jd_fit_score: float) -> dict:
        prompt = f"You are the Tech Lead. Give a ruthless 2-sentence verdict. Scores: Resume {resume_score}, GitHub {github_score}, JD {jd_fit_score}"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps(DebateResponse.model_json_schema())}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            return {"argument": "Error connecting to Tech Lead Agent.", "stance": "PASS"}

class HRAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model = "llama-3.1-8b-instant"

    def evaluate(self, linkedin_score: float, jd_fit_score: float) -> dict:
        prompt = f"You are the HR Partner. Give a 2-sentence verdict. Scores: LinkedIn {linkedin_score}, JD {jd_fit_score}"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps(DebateResponse.model_json_schema())}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            return {"argument": "Error connecting to HR Agent.", "stance": "PASS"}
"""
write_file("src/agents/debate_agents.py", debate)

# 7. Decider Agent
decider = """
import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class DeciderEvaluation(BaseModel):
    final_score: float = Field(description="The final weighted score out of 100.")
    status: str = Field(description="Must be exactly one of: HIRE, WAITLIST, REJECT")
    chat_message: str = Field(description="The final verdict message.")

class DeciderAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model = "llama-3.1-8b-instant"

    def make_decision(self, github_score: float, linkedin_score: float, resume_score: float, jd_score: float, tech_lead_argument: str, hr_argument: str) -> dict:
        raw_final = (resume_score * 0.5) + (github_score * 0.2) + (linkedin_score * 0.15) + (jd_score * 0.15)
        final_score_100 = round(raw_final * 10, 1)
        prompt = f"You are the Lead Hiring Manager. Math Score: {final_score_100}/100. Tech Lead: {tech_lead_argument}. HR: {hr_argument}. Output final decision."
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps(DeciderEvaluation.model_json_schema())}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            data = json.loads(chat_completion.choices[0].message.content)
            data["final_score"] = final_score_100
            if final_score_100 >= 80: data["status"] = "HIRE"
            elif final_score_100 >= 60: data["status"] = "WAITLIST"
            else: data["status"] = "REJECT"
            return data
        except Exception as e:
            return {"final_score": final_score_100, "status": "WAITLIST" if final_score_100 >= 60 else "REJECT", "chat_message": "Fallback decision."}
"""
write_file("src/agents/decider_agent.py", decider)
