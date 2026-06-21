import json
from pypdf import PdfReader
from src.agents.resume_agent import ResumeAgent

def run_test():
    agent = ResumeAgent()
    
    # Load your actual resume PDF
    pdf_path = r"C:\Users\Mahesh Babu\Downloads\test case  1.pdf"
    
    try:
        print(f"Extracting text from: {pdf_path}")
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return
        
    print("\n--- Running Resume Agent on Mahesh's Resume ---")
    result = agent.evaluate_resume(text, "Mahesh Nandigam")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    run_test()
