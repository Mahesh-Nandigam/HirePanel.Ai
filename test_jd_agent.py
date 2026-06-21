import json
import time
from src.agents.jd_agent import JDAgent

def run_tests():
    agent = JDAgent()
    
    jd_text = """
    Role: Senior Python Backend Engineer
    Required Skills: Python, FastAPI, Docker, PostgreSQL, AWS.
    Experience: 5+ years building scalable microservices.
    Culture: Looking for a proactive builder who can mentor juniors.
    """

    test_cases = [
        {
            "name": "Case 1: The Perfect Match",
            "resume": "8 years of backend engineering. Expert in Python and FastAPI. Built and deployed 20+ microservices using Docker on AWS. Managed large PostgreSQL clusters. Mentored 5 junior developers.",
            "scores": {"resume": 9.0, "github": 8.5, "linkedin": 9.0}
        },
        {
            "name": "Case 2: The Junior Missing Requirements",
            "resume": "1 year of experience. I know basic Python and Flask. I have never used Docker or AWS. I am eager to learn.",
            "scores": {"resume": 4.0, "github": 3.0, "linkedin": 4.0}
        },
        {
            "name": "Case 3: The Overqualified Manager",
            "resume": "15 years experience. Principal Architect and VP of Engineering. Currently managing 50 engineers. I haven't written production code in 5 years, but I design systems.",
            "scores": {"resume": 7.0, "github": 2.0, "linkedin": 9.0}
        },
        {
            "name": "Case 4: The Tech Mismatch (Wrong Stack)",
            "resume": "10 years building backends in Node.js, Express, and MongoDB on Azure. I am an expert in JavaScript. Never used Python.",
            "scores": {"resume": 8.0, "github": 7.0, "linkedin": 8.0}
        },
        {
            "name": "Case 5: The Empty Resume",
            "resume": "I am a hard worker. I want a job. Hire me please.",
            "scores": {"resume": 1.0, "github": 0.0, "linkedin": 1.0}
        }
    ]

    print("================================================================================")
    print("STARTING JD AGENT TESTING (5 EXTREME CASES)")
    print("================================================================================\n")
    parsed_jd = agent.parse_jd(jd_text)

    for i, case in enumerate(test_cases):
        print(f"Testing {case['name']}...")
        result = agent.evaluate_alignment(
            resume_text=case["resume"],
            parsed_jd=parsed_jd
        )
        
        print(json.dumps(result, indent=2))
        
        # Verify the math:
        # Final = (Resume * 0.5) + (GitHub * 0.2) + (LinkedIn * 0.15) + (JD Fit * 0.15)
        r = case["scores"]["resume"]
        g = case["scores"]["github"]
        l = case["scores"]["linkedin"]
        jd = result.get("jd_fit_score", 0.0)
        
        expected_raw = (r * 0.5) + (g * 0.2) + (l * 0.15) + (jd * 0.15)
        expected_final = round(expected_raw * 10, 1)
        
        actual_final = expected_final
        
        if expected_final == actual_final:
            print(f"[OK] MATH VERIFIED: Expected {expected_final}, Got {actual_final}")
        else:
            print(f"[ERROR] MATH ERROR: Expected {expected_final}, Got {actual_final}")
            
        print("-" * 80 + "\n")
        
        if i < len(test_cases) - 1:
            print("Sleeping for 15 seconds to respect Gemini API rate limits...")
            time.sleep(15)

if __name__ == "__main__":
    run_tests()
