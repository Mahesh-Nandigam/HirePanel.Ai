import json
from src.agents.linkedin_agent import LinkedInAgent

def run_tests():
    agent = LinkedInAgent()
    
    # Test Case 1: The Job Hopper
    hopper_resume = """
    JOHN HOPPER - Software Engineer
    
    Startup A (Jan 2023 - Aug 2023)
    - Wrote some React code.
    
    Startup B (Sep 2023 - Feb 2024)
    - Maintained legacy Angular app.
    
    Crypto Company C (Mar 2024 - Jul 2024)
    - Built a web3 dashboard.
    
    Agency D (Aug 2024 - Present)
    - Doing WordPress consulting.
    """

    # Test Case 2: The Loyal Employee with Promotions
    loyal_resume = """
    SARAH LOYAL - Senior Engineering Manager
    
    Tech Giant Inc.
    
    Senior Engineering Manager (Jan 2022 - Present)
    - Leading a team of 15 engineers across 3 squads.
    - Mentored 4 engineers to Senior level.
    
    Engineering Manager (Mar 2019 - Dec 2021)
    - Led the core payments team of 5 engineers.
    
    Senior Software Engineer (Jun 2016 - Feb 2019)
    - Architected the V2 of our primary microservices backend.
    
    Software Engineer (Aug 2014 - May 2016)
    - Built backend features using Python and Django.
    """

    print("================================================================================")
    print("TEST CASE 1: The Job Hopper")
    print("================================================================================")
    result_1 = agent.evaluate_profile(hopper_resume, "John Hopper")
    print(json.dumps(result_1, indent=2))
    
    print("\n\n")
    print("================================================================================")
    print("TEST CASE 2: The Loyal Employee (Promotions & Leadership)")
    print("================================================================================")
    result_2 = agent.evaluate_profile(loyal_resume, "Sarah Loyal")
    print(json.dumps(result_2, indent=2))

if __name__ == "__main__":
    run_tests()
