import os
import json
from src.agents.intake_agent import IntakeAgent

def run_test(pdf_path: str):
    print(f"Testing real PDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        print("File not found! Please check the path.")
        return
        
    agent = IntakeAgent()
    result = agent.parse_resume(pdf_path)
    
    print("\nExtraction Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    files = [
        r"C:\Users\Mahesh Babu\Downloads\Jillani Resume.pdf",
        r"C:\Users\Mahesh Babu\Downloads\Mehta.pdf",
        r"C:\Users\Mahesh Babu\Downloads\23J45A6616_PULAGARI SHIVA KUMAR REDDY_CSE-AIML.pdf"
    ]
    for test_file in files:
        run_test(test_file)
        print("="*40)
