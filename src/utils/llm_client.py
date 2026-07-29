import os
import time
import requests
from dotenv import load_dotenv

class MockChoiceMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockChatCompletion:
    def __init__(self, content):
        self.choices = [MockChoice(MockChoiceMessage(content))]

load_dotenv()

class NvidiaLLMClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NvidiaLLMClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def execute_completion(self, messages, model="meta/llama-3.3-70b-instruct", response_format=None, **kwargs):
        nvidia_api_key = os.environ.get("NVIDIA_API_KEY", "")
        if not nvidia_api_key.strip():
            raise Exception("NVIDIA_API_KEY is not set.")
            
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {nvidia_api_key}",
            "Content-Type": "application/json"
        }
        
        # Enforce NVIDIA reasoning model
        nvidia_model = model if "llama" in model.lower() else "meta/llama-3.3-70b-instruct"
        
        payload = {
            "model": nvidia_model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 4000)
        }
        if response_format:
            payload["response_format"] = response_format
            
        print(f"[NVIDIA API] Sending request to {nvidia_model}...")
        
        # Retry logic for NVIDIA API to handle rate limits and transient errors
        for attempt in range(3):
            start_time = time.time()
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30.0)
                latency = time.time() - start_time
                print(f"[NVIDIA API] Attempt {attempt+1}: Responded in {latency:.3f}s. Status: {response.status_code}")
                
                if response.status_code == 200:
                    res_data = response.json()
                    content = res_data["choices"][0]["message"]["content"]
                    return MockChatCompletion(content)
                elif response.status_code == 429:
                    print(f"[NVIDIA API] Rate limited. Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    print(f"[NVIDIA API Error {response.status_code}] {response.text}")
                    if response.status_code >= 500:
                        time.sleep(2)
                        continue
                    else:
                        raise Exception(f"NVIDIA API Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[NVIDIA API Connection Error] {e}")
                time.sleep(2)
        
        raise Exception(f"NVIDIA API failed after 3 attempts.")

# Singleton instance
llm_client = NvidiaLLMClient()
