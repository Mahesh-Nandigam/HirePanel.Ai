import json
from src.agents.linkedin_agent import LinkedInAgent

def run_tests():
    agent = LinkedInAgent()
    
    # TEST 1: JOB HOPPER
    t1 = """
    Startup A - Intern (4 months)
    Startup B - Software Engineer (5 months)
    Startup C - Software Engineer (6 months)
    Startup D - Software Engineer (7 months)
    Startup E - Software Engineer (5 months)
    """

    # TEST 2: TITLE INFLATOR
    t2 = """
    Junior Developer (1 year)
    Senior Developer (1 year)
    Principal Engineer (8 months)
    CTO (6 months)
    AI Visionary (4 months)
    """

    # TEST 3: LOYAL BUT STAGNANT
    t3 = """
    Software Engineer
    Company X
    2014-2024
    10 years
    No promotions
    No leadership
    """

    # TEST 4: FAST RISER
    t4 = """
    Intern (1 year)
    SDE-1 (1 year)
    SDE-2 (2 years)
    Senior Engineer (2 years)
    Engineering Manager (1 year)
    Same company (7 years total)
    """

    # TEST 5: FOUNDER TRAP
    t5 = """
    Founder & CEO
    Stealth Startup
    5 years
    No employees
    No funding
    No products
    
    Previous experience:
    6-month internship
    """

    tests = [
        ("TEST 1: JOB HOPPER", t1, "John Hopper"),
        ("TEST 2: TITLE INFLATOR", t2, "Tim Inflator"),
        ("TEST 3: LOYAL BUT STAGNANT", t3, "Loyal Larry"),
        ("TEST 4: FAST RISER", t4, "Rachel Riser"),
        ("TEST 5: FOUNDER TRAP", t5, "Frank Founder")
    ]

    for test_name, resume_text, candidate_name in tests:
        print("=" * 80)
        print(test_name)
        print("=" * 80)
        result = agent.evaluate_profile(resume_text, candidate_name)
        print(json.dumps(result, indent=2))
        print("\n\n")

if __name__ == "__main__":
    run_tests()
