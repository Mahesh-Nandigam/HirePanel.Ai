import os
import json
import re
import time
from pypdf import PdfReader
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from src.utils.groq_client import groq_rotator

load_dotenv()

class CandidateContext(BaseModel):
    candidate_name: str = Field(description="The full name of the candidate extracted from the resume. If not found, output 'Unknown'.")
    github_url: str = Field(description="Full GitHub profile URL. Return 'No' if not found.")
    linkedin_url: str = Field(description="Full LinkedIn profile URL. Return 'No' if not found.")
    resume_summary: str = Field(description="A comprehensive but compact summary of the candidate. List all technical skills, programming languages, total years of experience, and a detailed timeline of past jobs (employers, titles, dates, and brief key responsibilities). Maintain all critical factual details for vetting. Limit to 300 words.")

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

class IntakeAgent:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            reader = PdfReader(pdf_path)
            text = ""
            unique_links = set()
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                
                # Extract annotations (hyperlinks)
                if "/Annots" in page:
                    for annot in page["/Annots"]:
                        try:
                            obj = annot.get_object()
                            if obj and obj.get("/Subtype") == "/Link" and "/A" in obj:
                                action = obj["/A"].get_object()
                                if action and action.get("/S") == "/URI":
                                    uri = action.get("/URI")
                                    if uri:
                                        uri_clean = uri.strip()
                                        uri_lower = uri_clean.lower()
                                        if "github.com" in uri_lower or "linkedin.com" in uri_lower:
                                            unique_links.add(uri_clean)
                        except Exception as ann_err:
                            print(f"Error reading annotation: {ann_err}")
            
            # Compress extra whitespaces and empty lines to save tokens
            text = re.sub(r'[ \t]+', ' ', text)
            text = re.sub(r'\n+', '\n', text)
            text = text.strip()

            if unique_links:
                text += "\n--- Extracted Links ---\n"
                for link in sorted(unique_links):
                    text += f"{link}\n"
            return text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""

    def _extract_data_via_llm(self, text: str) -> dict:
        if not text.strip(): return {"candidate_name": "Unknown", "github_url": "No", "linkedin_url": "No", "resume_summary": ""}
        
        # 1. Regex for URLs (extremely fast and 100% accurate)
        github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+', text, re.IGNORECASE)
        linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', text, re.IGNORECASE)
        gh = github_match.group(0) if github_match else "No"
        li = linkedin_match.group(0) if linkedin_match else "No"

        # Sanitize URLs
        def sanitize_url(url, site):
            if not url or url.lower() in ["no", "none", "null", "n/a", "", "undefined"]:
                return "No"
            url_lower = url.lower()
            placeholders = ["username", "yourusername", "your-username", "[username]", "your_username", "user-name"]
            for placeholder in placeholders:
                if placeholder in url_lower:
                    return "No"
            if site == "github" and "github.com" not in url_lower:
                return "No"
            if site == "linkedin" and "linkedin.com" not in url_lower:
                return "No"
            return url

        gh = sanitize_url(gh, "github")
        li = sanitize_url(li, "linkedin")

        if gh and gh != "No":
            gh = gh.replace("www.", "").replace("https://", "").replace("http://", "").strip()
            if "github.com" not in gh:
                gh = "github.com/" + gh.lstrip("/")
            gh = "https://" + gh
            
        if li and li != "No":
            li = li.replace("www.", "").replace("https://", "").replace("http://", "").strip()
            if "linkedin.com" not in li:
                if li.startswith("in/"):
                    li = "linkedin.com/" + li
                else:
                    li = "linkedin.com/in/" + li.lstrip("/")
            li = "https://" + li

        gh = sanitize_url(gh, "github")
        li = sanitize_url(li, "linkedin")

        # 2. Heuristic for Name extraction (No LLM call)
        candidate_name = "Unknown"
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:10]:  # Look at the first 10 non-empty lines
            # Skip lines with email, social links, or phone patterns
            if "@" in line or "github.com" in line.lower() or "linkedin.com" in line.lower():
                continue
            if re.search(r'\+?\d{2,4}[-\s]?\d{3,5}[-\s]?\d{3,5}', line):
                continue
            if line.lower() in ["resume", "curriculum vitae", "cv", "portfolio", "contact", "about me", "profile"]:
                continue
            
            # Clean separators
            cleaned = line
            for sep in ['|', '-', '—', ',', '•']:
                if sep in cleaned:
                    parts = cleaned.split(sep)
                    if parts[0].strip():
                        cleaned = parts[0].strip()
            
            # Remove any special leading/trailing characters
            cleaned = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', cleaned).strip()
            # Verify it looks like a valid name (contains letters, not too long)
            if cleaned and any(c.isalpha() for c in cleaned) and len(cleaned) <= 40:
                candidate_name = cleaned
                break

        if candidate_name == "Unknown" and lines:
            candidate_name = lines[0]

        # Truncate text to 600 words to make it extremely token-efficient for downstream agents
        words = text.split()
        resume_summary = " ".join(words[:600])

        return {
            "candidate_name": candidate_name,
            "github_url": gh,
            "linkedin_url": li,
            "resume_summary": resume_summary
        }

    def parse_resume(self, pdf_path: str) -> dict:
        resume_filename = os.path.basename(pdf_path)
        resume_text = self.extract_text_from_pdf(pdf_path)
        if not resume_text.strip(): return {"candidate_name": "Unknown", "github_url": "No", "linkedin_url": "No", "resume_summary": "", "resume_filename": resume_filename}
        
        extracted = self._extract_data_via_llm(resume_text)
        extracted["resume_filename"] = resume_filename
        return extracted
