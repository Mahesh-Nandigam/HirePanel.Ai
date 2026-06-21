import json
from pypdf import PdfReader
from src.agents.intake_agent import IntakeAgent
from src.agents.github_agent import GitHubAgent
from src.agents.linkedin_agent import LinkedInAgent
from src.agents.resume_agent import ResumeAgent

def test_full_pipeline():
    pdf_path = r"C:\Users\Mahesh Babu\Downloads\23J45A6616_PULAGARI SHIVA KUMAR REDDY_CSE-AIML.pdf"
    
    print(f"Loading friend's resume: {pdf_path}\n")
    
    import time
    print("Waiting 10 seconds before starting...")
    time.sleep(10)
    
    # 1. Intake Agent
    print("================================================================================")
    print("1. INTAKE AGENT (Extracting URLs and Name)")
    print("================================================================================")
    intake = IntakeAgent()
    candidate_info = intake.parse_resume(pdf_path)
    print(json.dumps(candidate_info, indent=2))
    
    name = candidate_info.get("candidate_name", "Candidate")
    github_url = candidate_info.get("github_url", "No")
    
    # Extract raw text for the other agents
    text = intake.extract_text_from_pdf(pdf_path)

    import time
    
    # 2. GitHub Agent
    time.sleep(10)
    print("\n\n================================================================================")
    print("2. GITHUB AGENT (Evaluating open source contributions)")
    print("================================================================================")
    if github_url != "No":
        github_agent = GitHubAgent()
        github_result = github_agent.evaluate_profile(github_url)
        print(json.dumps(github_result, indent=2))
    else:
        print("No GitHub URL found. Assigning 0.0.")

    # 3. LinkedIn (Career) Agent
    time.sleep(10)
    print("\n\n================================================================================")
    print("3. LINKEDIN AGENT (Evaluating career stability & promotions)")
    print("================================================================================")
    linkedin_agent = LinkedInAgent()
    linkedin_result = linkedin_agent.evaluate_profile(text, name)
    print(json.dumps(linkedin_result, indent=2))

    # 4. Resume Agent
    time.sleep(10)
    print("\n\n================================================================================")
    print("4. RESUME AGENT (Evaluating execution and project impact)")
    print("================================================================================")
    resume_agent = ResumeAgent()
    resume_result = resume_agent.evaluate_resume(text, name)
    print(json.dumps(resume_result, indent=2))


if __name__ == "__main__":
    test_full_pipeline()
