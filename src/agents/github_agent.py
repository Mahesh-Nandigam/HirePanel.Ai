import os
import json
import requests
import re
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from src.utils.groq_client import groq_rotator

load_dotenv()

class GitHubContext(BaseModel):
    github_score: float = Field(description="Overall technical score out of 10.0.")
    chat_message: str = Field(description="A dynamic natural-language message sounding like a Senior Engineering Manager summarizing their open-source presence.")

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

class GitHubAgent:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token: self.headers["Authorization"] = f"token {self.github_token}"
        self.demo_mode = os.environ.get("DEMO_MODE", "").lower() == "true"

    def extract_username(self, github_url: str) -> str:
        if github_url.lower() == "no": return ""
        match = re.search(r'github\.com/([A-Za-z0-9_-]+)', github_url, re.IGNORECASE)
        return match.group(1) if match else ""

    def fetch_github_data(self, username: str) -> dict:
        if not username or self.demo_mode: return {}
        base_url = f"https://api.github.com/users/{username}"
        data = {}
        try:
            prof_resp = requests.get(base_url, headers=self.headers, timeout=5)
            if prof_resp.status_code == 200:
                prof = prof_resp.json()
                data['profile'] = {"followers": prof.get("followers", 0), "public_repos": prof.get("public_repos", 0), "bio": prof.get("bio", ""), "created_at": prof.get("created_at", "")}
                repos_resp = requests.get(f"{base_url}/repos?sort=updated&per_page=30", headers=self.headers, timeout=5)
                if repos_resp.status_code == 200:
                    data['repositories'] = [{"name": r.get("name"), "stars": r.get("stargazers_count", 0), "fork": r.get("fork", False), "language": r.get("language"), "description": r.get("description", "")} for r in repos_resp.json()]
                events_resp = requests.get(f"{base_url}/events?per_page=30", headers=self.headers, timeout=5)
                if events_resp.status_code == 200:
                    events = events_resp.json()
                    data['recent_activity'] = {"total_recent_events": len(events), "recent_pushes": len([e for e in events if e.get("type") == "PushEvent"])}
            else:
                print(f"GitHub API returned {prof_resp.status_code} for {username}.")
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")
        return data

    def evaluate_profile(self, github_url: str, resume_text: str = "", candidate_name: str = "") -> dict:
        username = self.extract_username(github_url)
        empty_resp = {"github_score": 0.0, "chat_message": "No valid GitHub profile provided."}

        api_data = self.fetch_github_data(username) if username else {}

        if api_data and 'profile' in api_data:
            # Live GitHub data available
            prompt = (
                f"Evaluate {candidate_name}'s open-source footprint mathematically and qualitatively.\n"
                f"Raw GitHub Data:\n{json.dumps(api_data, indent=2)}\n\n"
                f"Scoring: Assess commit consistency, project quality (stars, complexity), and special achievements.\n"
                f"Do NOT invent any details not in the raw data."
            )
        elif resume_text.strip():
            # Resume inference mode - extract engineering signals from resume
            resume_snippet = " ".join(resume_text.split()[:500])
            prompt = (
                f"You are a Senior Engineering Manager. Evaluate {candidate_name}'s likely CODE QUALITY and ENGINEERING CAPABILITY based ONLY on their resume.\n\n"
                f"Resume Evidence:\n{resume_snippet}\n\n"
                f"Analyze these specific signals from the resume:\n"
                f"1. PROJECT COMPLEXITY: Are there production systems, microservices, or just CRUD apps?\n"
                f"2. AI/ML DEPTH: RAG pipelines, vector databases, LLM fine-tuning, multi-agent systems?\n"
                f"3. DEPLOYMENT EVIDENCE: Docker, CI/CD, cloud deployment (AWS/GCP/Azure), Kubernetes?\n"
                f"4. ARCHITECTURE: System design patterns, scalable architectures, API design?\n"
                f"5. OPEN-SOURCE SIGNALS: GitHub links, contributions mentioned, portfolio projects?\n"
                f"6. TECH STACK BREADTH: How many frameworks/languages with demonstrated proficiency?\n\n"
                f"Scoring Guide:\n"
                f"- 9-10: Production AI systems + complex architectures + deployment pipelines + open-source\n"
                f"- 7-8: Full-stack projects with real deployments + multiple frameworks\n"
                f"- 5-6: Academic/personal projects + limited deployment evidence\n"
                f"- 3-4: Only coursework or tutorial-level projects\n\n"
                f"Your chat_message MUST reference SPECIFIC projects, technologies, or patterns from the resume. Never be generic."
            )
        else:
            return empty_resp

        try:
            chat_completion = groq_rotator.execute_completion(
                messages=[
                    {"role": "system", "content": "You are a JSON assistant. Output valid JSON."},
                    {"role": "user", "content": prompt + "\nOutput JSON exactly matching this format:\n" + get_simple_schema(GitHubContext)}
                ],
                model=self.model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"GitHub Agent Error: {e}")
            return empty_resp
