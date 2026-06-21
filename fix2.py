import os
import re

def fix_file(filepath, schema_name):
    with open(filepath, "r") as f:
        content = f.read()
    
    pattern = r"            response = self\.model\.generate_content\([\s\S]*?response_schema=[A-Za-z0-9_]+,[\s\S]*?\)\n\s*data = json\.loads\(response\.text\)"
    
    repl = f"""            chat_completion = self.client.chat.completions.create(
                messages=[
                    {{"role": "system", "content": "You are a JSON assistant. Output valid JSON."}},
                    {{"role": "user", "content": prompt + "\\nOutput JSON exactly matching this schema:\\n" + json.dumps({schema_name}.model_json_schema())}}
                ],
                model=self.model,
                response_format={{"type": "json_object"}},
            )
            data = json.loads(chat_completion.choices[0].message.content)"""
    
    new_content = re.sub(pattern, repl, content)
    with open(filepath, "w") as f:
        f.write(new_content)

fix_file("src/agents/jd_agent.py", "JDEvaluation")
fix_file("src/agents/decider_agent.py", "DeciderEvaluation")
fix_file("src/agents/resume_agent.py", "ResumeEvaluation")
print("Fixed!")
