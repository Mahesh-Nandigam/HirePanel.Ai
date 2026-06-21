import json
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

def run_pipeline(pdf_path: str, job_description: str):
    print(f"--- STARTING FULL PIPELINE TEST FOR: {pdf_path} ---")
    
    # 1. Intake Agent
    print("\n[1/7] Running Intake Agent...")
    intake = IntakeAgent()
    candidate_info = intake.parse_resume(pdf_path)
    name = candidate_info.get("candidate_name", "Unknown")
    github_url = candidate_info.get("github_url", "No")
    print(f"Extracted Name: {name}")
    print(f"Extracted GitHub: {github_url}")
    
    # Read text
    text = intake.extract_text_from_pdf(pdf_path)

    # 2. GitHub Agent
    print("\n[2/7] Running GitHub Agent...")
    github_result = {"github_score": 0.0, "chat_message": "No GitHub URL found.", "strengths": [], "concerns": []}
    if github_url != "No":
        github_agent = GitHubAgent()
        github_result = github_agent.evaluate_profile(github_url)
    github_score = safe_float(github_result.get("github_score", 0.0))
    print(f"GitHub Score: {github_score}/10")

    # 3. LinkedIn Agent
    print("\n[3/7] Running LinkedIn Agent...")
    linkedin_agent = LinkedInAgent()
    linkedin_result = linkedin_agent.evaluate_profile(text, name)
    linkedin_score = safe_float(linkedin_result.get("linkedin_score", 0.0))
    print(f"LinkedIn Score: {linkedin_score}/10")

    # 4. Resume Agent
    print("\n[4/7] Running Resume Agent...")
    resume_agent = ResumeAgent()
    resume_result = resume_agent.evaluate_resume(text, name)
    resume_score = safe_float(resume_result.get("resume_score", 0.0))
    print(f"Resume Score: {resume_score}/10")

    # 5. JD Agent (Alignment)
    print("\n[5/7] Running JD Agent...")
    jd_agent = JDAgent()
    parsed_jd = jd_agent.parse_jd(job_description)
    jd_result = jd_agent.evaluate_alignment(text, parsed_jd)
    jd_score = safe_float(jd_result.get("jd_fit_score", 0.0))
    print(f"JD Fit Score: {jd_score}/10")

    # 6. Debate Agents
    print("\n[6/7] Running Tech Lead and HR Debate Agents...")
    tech_lead = TechLeadAgent()
    hr_agent = HRAgent()
    
    tl_result = tech_lead.evaluate(resume_score, github_score, jd_score)
    hr_result = hr_agent.evaluate(linkedin_score, jd_score)
    
    tl_arg = tl_result.get("argument", "No strong technical opinion.")
    hr_arg = hr_result.get("argument", "No strong HR opinion.")
    print(f"Tech Lead Argument: {tl_arg}")
    print(f"HR Argument: {hr_arg}")

    # 7. Decider Agent
    print("\n[7/7] Running Decider Agent (Final Verdict)...")
    decider = DeciderAgent()
    final_verdict = decider.make_decision(github_score, linkedin_score, resume_score, jd_score, tl_arg, hr_arg)
    
    final_score_100 = final_verdict.get("final_score", 0.0)
    status = final_verdict.get("status", "REJECT")
    decider_msg = final_verdict.get("chat_message", "No final verdict generated.")

    print("\n==================================================")
    print("FINAL RESULTS")
    print("==================================================")
    print(f"Name: {name}")
    print(f"Status: {status}")
    print(f"Final Score: {final_score_100}/100")
    print(f"Decider Message: {decider_msg}")
    print("==================================================\n")
    print("Pipeline Test Completed Successfully!")

if __name__ == "__main__":
    job_desc = "Looking for a Software Engineer with Python and AWS experience."
    run_pipeline(r"C:\Users\Mahesh Babu\Downloads\Jillani Resume.pdf", job_desc)
