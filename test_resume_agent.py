import json
from src.agents.resume_agent import ResumeAgent

def run_tests():
    agent = ResumeAgent()
    
    # TEST 1: BUZZWORD COLLECTOR
    t1 = """
    Skills: Python, Java, React, Node, AWS, Docker, Kubernetes, TensorFlow, C++, Go, Rust
    
    Projects:
    - Calculator App: Made a basic calculator using HTML/CSS/JS.
    - ToDo App: A ToDo app where you can add and delete items.
    """

    # TEST 2: REAL BUILDER
    t2 = """
    Skills: Python, FastAPI, WebSockets, LLMs
    
    Projects:
    - AI Recruitment Platform: Built an autonomous agentic system using FastAPI, Gemini API, and WebSockets. Deployed to AWS via Docker. Handled 500+ concurrent connections during load testing.
    
    Achievements:
    - 1st Place Winner at Global AI Hackathon (out of 500 teams).
    """

    # TEST 3: ACADEMIC GENIUS
    t3 = """
    Education: PhD in Machine Learning
    
    Publications:
    - "A Novel Approach to Latent Space Regularization" - Published in NeurIPS.
    - "Attention Mechanisms in Deep Vision" - Published in IEEE.
    
    No projects or software engineering experience listed.
    """

    # TEST 4: OPEN SOURCE WARRIOR
    t4 = """
    Experience:
    - Core Maintainer of popular open source Python framework.
    - Over 200 merged PRs addressing complex architectural bottlenecks and memory leaks.
    - Authored the asynchronous request module.
    """

    # TEST 5: RESUME INFLATOR
    t5 = """
    Skills: [50 buzzwords listed]
    
    Experience: 
    - Nothing listed.
    
    Projects: 
    - Nothing listed.
    
    Achievements: 
    - Nothing listed.
    """

    tests = [
        ("TEST 1: BUZZWORD COLLECTOR", t1, "Bob Buzzword"),
        ("TEST 2: REAL BUILDER", t2, "Betty Builder"),
        ("TEST 3: ACADEMIC GENIUS", t3, "Albert Academic"),
        ("TEST 4: OPEN SOURCE WARRIOR", t4, "Oliver OpenSource"),
        ("TEST 5: RESUME INFLATOR", t5, "Ian Inflator")
    ]

    for test_name, resume_text, candidate_name in tests:
        print("=" * 80)
        print(test_name)
        print("=" * 80)
        result = agent.evaluate_resume(resume_text, candidate_name)
        print(json.dumps(result, indent=2))
        print("\n\n")
        import time
        time.sleep(15) # Sleep to avoid Gemini free tier rate limits (15 RPM)

if __name__ == "__main__":
    run_tests()
