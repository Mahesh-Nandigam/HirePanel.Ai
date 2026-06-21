import json
from src.agents.jd_agent import JDAgent

tests = {
    "Test 1 - Perfect Structured JD": """
Senior Backend Engineer

Required Skills:
- Python
- FastAPI
- PostgreSQL

Preferred Skills:
- Docker
- AWS

Experience:
5+ years

Domain:
FinTech
""",
    "Test 2 - Messy Recruiter JD": """
URGENT HIRING!!!

Need React developer ASAP.

Good knowledge of React, JS, TS.

Nice if knows Next.js.

Freshers can apply.
""",
    "Test 3 - AI/ML Role": """
Principal AI Research Scientist

Must Have:
PyTorch
CUDA
Transformers

Experience:
8-10 years

Preferred:
Vector Databases
AWS

Domain:
Cybersecurity SaaS
""",
    "Test 4 - Very Small JD": """
Need Python Developer.
""",
    "Test 5 - Data Science JD": """
Looking for Data Scientist.

Requirements:
Python
Pandas
Machine Learning
SQL

3-5 years experience.

Healthcare industry.
""",
    "Test 6 - Weird LinkedIn Copy-Paste": """
About the job

Join our growing startup!

What you'll do:
Build scalable APIs.
Work with Python and FastAPI.

What we're looking for:
3+ years experience.
"""
}

def run_tests():
    agent = JDAgent()
    
    for name, jd_text in tests.items():
        print(f"\n{'='*50}")
        print(f"Running: {name}")
        print(f"{'='*50}")
        
        try:
            result = agent.parse_jd(jd_text)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"CRASH: {e}")

if __name__ == "__main__":
    run_tests()
