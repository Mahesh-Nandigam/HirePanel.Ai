import os
import time
import requests
import re
from dotenv import load_dotenv

class MockChoiceMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockChoiceMessage(content)

class MockChatCompletion:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

load_dotenv()

class GroqKeyRotator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GroqKeyRotator, cls).__new__(cls, *args, **kwargs)
            cls._instance._init_rotator()
        return cls._instance

    def _init_rotator(self):
        self.keys = []
        # Load primary key
        primary = os.environ.get("GROQ_API_KEY", "")
        if primary.strip():
            self.keys.append(primary.strip())
        
        # Load extra keys
        for i in range(1, 10):
            extra = os.environ.get(f"GROQ_API_KEY_{i}", "")
            if extra.strip():
                self.keys.append(extra.strip())
        
        # Ensure we have at least one key
        if not self.keys:
            print("WARNING: No Groq API keys loaded from environment!")
        
        self.current_idx = 0
        self.demo_mode = os.environ.get("DEMO_MODE", "").lower() == "true"

        if self.demo_mode:
            self.ollama_active = False
            print("[DEMO MODE] Groq cloud only. Ollama bypassed for maximum speed.")
        else:
            self.ollama_active = True
            self.last_ollama_fail = 0
            # Preload Ollama model to prevent cold start latency
            try:
                print("Preloading Ollama model (gemma3:4b)...")
                requests.post("http://127.0.0.1:11434/api/generate", json={"model": "gemma3:4b", "keep_alive": -1}, timeout=3.0)
            except Exception as e:
                print(f"Ollama preloading skipped/failed: {e}")

    def _call_ollama(self, messages, response_format=None):
        url = "http://127.0.0.1:11434/v1/chat/completions"
        payload = {
            "model": "gemma3:4b",
            "messages": messages,
            "temperature": 0.2
        }
        if response_format:
            payload["response_format"] = response_format

        start_time = time.time()
        print(f"[Ollama Request] Sending request to gemma3:4b model...")
        response = requests.post(url, json=payload, timeout=(5.0, 120.0))
        latency = time.time() - start_time
        print(f"[Ollama Response] gemma3:4b responded in {latency:.3f}s. Status: {response.status_code}")

        if response.status_code == 200:
            res_data = response.json()
            content = res_data["choices"][0]["message"]["content"]
            
            # Sanitize markdown code block formatting in JSON outputs if present
            if response_format and response_format.get("type") == "json_object":
                content_clean = content.strip()
                if content_clean.startswith("```"):
                    match = re.search(r'```(?:json)?\s*(.*?)\s*```', content_clean, re.DOTALL | re.IGNORECASE)
                    if match:
                        content = match.group(1).strip()
                
                # Check for empty response or invalid JSON structures
                try:
                    import json
                    parsed = json.loads(content)
                    if not parsed or (isinstance(parsed, dict) and not parsed):
                        raise Exception("Local Ollama returned an empty JSON dictionary.")
                except Exception as je:
                    raise Exception(f"Local Ollama returned malformed or empty JSON: {je}. Raw response was: {content}")
            
            return MockChatCompletion(content)
        else:
            raise Exception(f"Ollama returned status code {response.status_code}")

    def execute_completion(self, messages, model="llama-3.3-70b-versatile", response_format=None, **kwargs):
        is_groq_disabled = os.environ.get("DISABLE_GROQ_FALLBACK", "").lower() == "true"

        if is_groq_disabled:
            # Strict local Ollama-only path (no fallback to Groq)
            try:
                # Fast ping check to verify Ollama is active (timeout 1.0s)
                ping_resp = requests.get("http://127.0.0.1:11434/", timeout=1.0)
                if ping_resp.status_code != 200 or "ollama is running" not in ping_resp.text.lower():
                    raise Exception("Ollama signature not found in response text")
            except Exception as e:
                raise Exception(f"Ollama is offline/unreachable and Groq fallback is disabled: {e}")

            try:
                return self._call_ollama(messages, response_format)
            except Exception as e:
                raise Exception(f"Ollama inference failed: {e}")

        # Re-enable Ollama check if 60 seconds have passed since last failure
        if not self.demo_mode and not self.ollama_active:
            if time.time() - self.last_ollama_fail > 60:
                self.ollama_active = True

        # Fast ping check to verify Ollama is active and responding (timeout 1.0s)
        if self.ollama_active:
            try:
                ping_resp = requests.get("http://127.0.0.1:11434/", timeout=1.0)
                if ping_resp.status_code != 200 or "ollama is running" not in ping_resp.text.lower():
                    raise Exception("Ollama signature not found in response text")
            except Exception as e:
                print(f"Ollama local ping failed: {e}. Disabling local inference for 60 seconds.")
                self.ollama_active = False
                self.last_ollama_fail = time.time()

        # 1. Attempt local Ollama inference first (if online)
        if self.ollama_active:
            try:
                return self._call_ollama(messages, response_format)
            except Exception as e:
                print(f"Ollama inference error: {e}")
                print("Falling back to Groq...")

        nvidia_api_key = os.environ.get("NVIDIA_API_KEY") 
        if not nvidia_api_key:
            raise Exception("NVIDIA_API_KEY environment variable is not set!")
        # Using a fallback key if not present in env, though we can also just use the one we know works.
        # Actually, let's just use the direct request to NVIDIA
        
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {nvidia_api_key}",
            "Content-Type": "application/json"
        }
        
        # We enforce the 8B model for maximum speed
        nvidia_model = "meta/llama-3.1-8b-instruct"
        
        payload = {
            "model": nvidia_model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 4000)
        }
        if response_format:
            payload["response_format"] = response_format
            
        print(f"[NVIDIA API] Sending request to {nvidia_model}...")
        start_time = time.time()
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30.0)
            latency = time.time() - start_time
            print(f"[NVIDIA API] Responded in {latency:.3f}s. Status: {response.status_code}")
            
            if response.status_code == 200:
                res_data = response.json()
                content = res_data["choices"][0]["message"]["content"]
                return MockChatCompletion(content)
            else:
                raise Exception(f"NVIDIA API Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[NVIDIA API ERROR] {e}")
            raise e

# Singleton instance
groq_rotator = GroqKeyRotator()
