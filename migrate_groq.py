import os
import re
import glob

files = glob.glob("src/agents/*.py")

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace import
    content = content.replace("import google.generativeai as genai", "from groq import Groq")
    
    # Replace init
    init_pattern = r"""        api_key = os\.environ\.get\("GEMINI_API_KEY", ""\)\n\s*if api_key:\n\s*genai\.configure\(api_key=api_key\)\n\s*self\.model = genai\.GenerativeModel\("gemini-2\.5-flash"\)"""
    new_init = """        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))\n        self.model = "llama3-8b-8192" """
    content = re.sub(init_pattern, new_init, content)
    
    # Also handle debate_agents.py which has multiple classes
    content = content.replace('api_key = os.environ.get("GEMINI_API_KEY", "")\n        if api_key:\n            genai.configure(api_key=api_key)\n        self.model = genai.GenerativeModel("gemini-2.5-flash")', 
                              'self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))\n        self.model = "llama3-8b-8192"')

    # Replace generate_content block
    generate_pattern = r"""            response = self\.model\.generate_content\(\n\s*prompt,\n\s*generation_config=genai\.GenerationConfig\(\n\s*response_mime_type="application/json",\n\s*response_schema=([A-Za-z0-9_]+),\n\s*\),\n\s*\)\n\s*(?:return json\.loads\(response\.text\)|data = json\.loads\(response\.text\)\n\s*return data\.get\("candidate_name", "Unknown"\))"""
    
    def replacer(match):
        schema_name = match.group(1)
        if "candidate_name" in match.group(0):
            return f"""            chat_completion = self.client.chat.completions.create(
                messages=[
                    {{"role": "system", "content": "You are a JSON assistant. Output valid JSON."}},
                    {{"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps({schema_name}.model_json_schema())}}
                ],
                model=self.model,
                response_format={{"type": "json_object"}},
            )
            data = json.loads(chat_completion.choices[0].message.content)
            return data.get("candidate_name", "Unknown")"""
        else:
            return f"""            chat_completion = self.client.chat.completions.create(
                messages=[
                    {{"role": "system", "content": "You are a JSON assistant. Output valid JSON."}},
                    {{"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps({schema_name}.model_json_schema())}}
                ],
                model=self.model,
                response_format={{"type": "json_object"}},
            )
            return json.loads(chat_completion.choices[0].message.content)"""
            
    content = re.sub(generate_pattern, replacer, content)

    # Some agent files have custom LLM error messages, we just make sure Groq is used.
    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Migration completed!")
