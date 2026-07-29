from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import asyncio
from pypdf import PdfReader

def safe_float(val):
    try:
        if isinstance(val, str):
            import re
            match = re.search(r"[\d\.]+", val)
            return float(match.group(0)) if match else 0.0
        return float(val)
    except:
        return 0.0

from src.agents.intake_agent import IntakeAgent
from src.agents.github_agent import GitHubAgent
from src.agents.linkedin_agent import LinkedInAgent
from src.agents.resume_agent import ResumeAgent
from src.agents.jd_agent import JDAgent
from src.agents.debate_agents import TechLeadAgent, HRAgent
from src.agents.decider_agent import DeciderAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/intake")
async def process_intake(file: UploadFile = File(...)):
    temp_path = f"temp_intake_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        intake = IntakeAgent()
        candidate_info = intake.parse_resume(temp_path)
        return {
            "resume_filename": file.filename,
            "candidate_name": candidate_info.get("candidate_name", "Unknown"),
            "github_url": candidate_info.get("github_url", "No"),
            "linkedin_url": candidate_info.get("linkedin_url", "No")
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

jd_cache_lock = asyncio.Lock()
parsed_jd_cache = {}

@app.post("/api/evaluate")
async def evaluate_candidate(file: UploadFile = File(...), job_description: str = Form("We are looking for a great Software Engineer.")):
    import time
    start_total = time.time()
    
    # 1. Intake Agent
    start_intake = time.time()
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        intake = IntakeAgent()
        candidate_info = intake.parse_resume(temp_path)
        name = candidate_info.get("candidate_name", "Unknown")
        github_url = candidate_info.get("github_url", "No")
        linkedin_url = candidate_info.get("linkedin_url", "No")
        resume_summary = candidate_info.get("resume_summary", "")
        
        # Use token-efficient resume summary if available, otherwise fallback to full parsed text
        text = resume_summary if resume_summary.strip() else intake.extract_text_from_pdf(temp_path)
        intake_time = time.time() - start_intake

        # 2. JD Parsing (Cached with asyncio.Lock to prevent race condition)
        start_jd_parsing = time.time()
        jd_key = job_description.strip()
        async with jd_cache_lock:
            if jd_key not in parsed_jd_cache:
                jd_agent = JDAgent()
                # Run the blocking parse_jd call in a separate thread
                parsed_jd = await asyncio.to_thread(jd_agent.parse_jd, job_description)
                parsed_jd_cache[jd_key] = parsed_jd
            else:
                parsed_jd = parsed_jd_cache[jd_key]
        jd_parsing_time = time.time() - start_jd_parsing
        
        # 3. Run GitHub, LinkedIn, Resume, and JD agents in parallel
        start_assessors = time.time()

        def run_github():
            return GitHubAgent().evaluate_profile(github_url, resume_text=text, candidate_name=name)

        def run_linkedin():
            return LinkedInAgent().evaluate_profile(text, name, linkedin_url)

        def run_resume():
            return ResumeAgent().evaluate_resume(text, name)

        def run_jd():
            return JDAgent().evaluate_alignment(text, parsed_jd)

        github_result, linkedin_result, resume_result, jd_result = await asyncio.gather(
            asyncio.to_thread(run_github),
            asyncio.to_thread(run_linkedin),
            asyncio.to_thread(run_resume),
            asyncio.to_thread(run_jd)
        )
        assessors_time = time.time() - start_assessors

        resume_score = safe_float(resume_result.get("resume_score", 0.0))
        github_score = safe_float(github_result.get("github_score", 0.0))
        linkedin_score = safe_float(linkedin_result.get("linkedin_score", 0.0))
        jd_score = safe_float(jd_result.get("jd_fit_score", 0.0))

        # 4. Run Tech Lead and HR debate agents in a sequential debate loop
        start_debate = time.time()
        # Build richer resume context for debate agents (up to 1500 words)
        resume_context = " ".join(text.split()[:1500])

        # Step A: Get initial Technical evaluation from the Tech Lead
        tl_initial = await asyncio.to_thread(
            TechLeadAgent().evaluate, resume_score, github_score, jd_score, name, resume_context
        )
        tl_init_arg = tl_initial.get("argument", "No strong technical opinion.")
        tl_init_stance = tl_initial.get("stance", "PASS")

        # Step B: Pass Tech Lead's argument to the HR Partner for their counter-evaluation
        hr_result = await asyncio.to_thread(
            HRAgent().evaluate, linkedin_score, jd_score, name, resume_context, peer_argument=tl_init_arg, peer_stance=tl_init_stance
        )
        hr_arg = hr_result.get("argument", "No strong HR opinion.")
        hr_stance = hr_result.get("stance", "PASS")

        # Step C: Pass HR Partner's counter-argument back to the Tech Lead for a final response/rebuttal
        tl_result = await asyncio.to_thread(
            TechLeadAgent().evaluate, resume_score, github_score, jd_score, name, resume_context, peer_argument=hr_arg, peer_stance=hr_stance
        )
        tl_arg = tl_result.get("argument", "No strong technical opinion.")
        debate_time = time.time() - start_debate

        # 5. Decider Agent
        start_decider = time.time()
        decider = DeciderAgent()
        final_verdict = decider.make_decision(github_score, linkedin_score, resume_score, jd_score, tl_arg, hr_arg)
        
        final_score_100 = final_verdict.get("final_score", 0.0)
        status = final_verdict.get("status", "REJECT")
        decider_msg = final_verdict.get("chat_message", "No final verdict generated.")
        decider_time = time.time() - start_decider

        total_time = time.time() - start_total

        print(f"\n==============================================")
        print(f"TIMING BREAKDOWN FOR CANDIDATE: {name}")
        print(f"==============================================")
        print(f"Intake Phase:        {intake_time:.3f}s")
        print(f"JD Parsing Phase:    {jd_parsing_time:.3f}s")
        print(f"Assessor Agents:     {assessors_time:.3f}s")
        print(f"Debate Agents:       {debate_time:.3f}s")
        print(f"Decider Agent:       {decider_time:.3f}s")
        print(f"----------------------------------------------")
        print(f"Total Pipeline Time: {total_time:.3f}s")
        print(f"==============================================\n")

        # Construct payload for UI
        payload = {
            "name": name,
            "role": "Software Engineer",
            "finalScore": final_score_100,
            "github": github_score,
            "linkedin": linkedin_score,
            "resume": resume_score,
            "jdMatch": jd_score,
            "status": status,
            "avatar": f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=random&color=fff",
            "strengths": jd_result.get("strengths", []),
            "messages": [
                { "agent": "Intake", "text": f"Parsed resume for {name}. Extracted GitHub: {github_url}" },
                { "agent": "Resume", "text": resume_result.get("chat_message", "No analysis.") },
                { "agent": "GitHub", "text": github_result.get("chat_message", "No analysis.") },
                { "agent": "LinkedIn", "text": linkedin_result.get("chat_message", "No analysis.") },
                { "agent": "Tech Lead", "text": tl_arg },
                { "agent": "HR", "text": hr_arg },
                { "agent": "Decider", "text": f"[Pipeline Time: {total_time:.2f}s] {decider_msg}" }
            ],
            "timings": {
                "intake": round(intake_time, 2),
                "jd_parsing": round(jd_parsing_time, 2),
                "assessors": round(assessors_time, 2),
                "debate": round(debate_time, 2),
                "decider": round(decider_time, 2),
                "total": round(total_time, 2)
            }
        }
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return payload
