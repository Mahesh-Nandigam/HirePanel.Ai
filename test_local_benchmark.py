import asyncio
import time
import os
import httpx
import psutil
import threading
from dotenv import load_dotenv

load_dotenv()

# Enforce no Groq fallback during this benchmark run
os.environ["DISABLE_GROQ_FALLBACK"] = "True"

API_URL = "http://127.0.0.1:8001/api/evaluate"
OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"

CANDIDATES = [
    {"name": "Jillani", "path": r"C:\Users\Mahesh Babu\Downloads\Jillani Resume.pdf"},
    {"name": "Mehta", "path": r"C:\Users\Mahesh Babu\Downloads\Mehta.pdf"},
    {"name": "Shiva Kumar", "path": r"C:\Users\Mahesh Babu\Downloads\23J45A6616_PULAGARI SHIVA KUMAR REDDY_CSE-AIML.pdf"}
]

cpu_measurements = []
mem_measurements = []
monitoring = True

def monitor_resources():
    global cpu_measurements, mem_measurements, monitoring
    while monitoring:
        try:
            cpu_measurements.append(psutil.cpu_percent(interval=0.5))
            mem_measurements.append(psutil.virtual_memory().percent)
        except Exception:
            pass

async def preload_ollama():
    print("Pre-warming Ollama model 'gemma3:4b' and keeping it resident...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(OLLAMA_GENERATE_URL, json={"model": "gemma3:4b", "keep_alive": -1}, timeout=10.0)
            if resp.status_code == 200:
                print("[OK] Ollama model preloaded and resident.")
            else:
                print(f"[WARN] Preload endpoint returned status: {resp.status_code}")
        except Exception as e:
            print(f"[WARN] Failed to preload Ollama model: {e}")

async def evaluate_candidate(client, name, path, job_desc):
    print(f"[START] Triggering evaluation for: {name}...")
    start_time = time.time()
    
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f, "application/pdf")}
        data = {"job_description": job_desc}
        
        try:
            # Connect/read timeouts set to 300s to allow Ollama server-side queuing to complete
            resp = await client.post(API_URL, files=files, data=data, timeout=300.0)
            elapsed = time.time() - start_time
            if resp.status_code == 200:
                payload = resp.json()
                print(f"[SUCCESS] Candidate {name} completed in {elapsed:.2f}s")
                return {"name": name, "success": True, "elapsed": elapsed, "payload": payload}
            else:
                print(f"[FAILED] Candidate {name} failed with status {resp.status_code}: {resp.text}")
                return {"name": name, "success": False, "elapsed": elapsed, "error": resp.text}
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            elapsed = time.time() - start_time
            print(f"[ERROR] Candidate {name} raised exception after {elapsed:.2f}s:\n{tb}")
            return {"name": name, "success": False, "elapsed": elapsed, "error": tb}

async def run_benchmark():
    global monitoring
    
    # Pre-load Ollama model to lock it into memory
    await preload_ollama()
    
    job_desc = (
        "Role: Senior Python Backend Engineer\n"
        "Required Skills: Python, FastAPI, Docker, PostgreSQL, AWS, Git, REST APIs\n"
        "Experience: 5+ years building scalable microservices and database optimization.\n"
        "Culture: Looking for a proactive builder."
    )
    
    print("\nStarting system-wide CPU/Memory resource monitoring...")
    monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
    monitor_thread.start()
    
    print(f"\nExecuting concurrent evaluations of {len(CANDIDATES)} candidates...")
    start_bench = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = [evaluate_candidate(client, c["name"], c["path"], job_desc) for c in CANDIDATES]
        results = await asyncio.gather(*tasks)
        
    end_bench = time.time()
    total_elapsed = end_bench - start_bench
    
    # Terminate monitoring thread
    monitoring = False
    monitor_thread.join()
    
    # Calculate stats
    avg_cpu = sum(cpu_measurements) / len(cpu_measurements) if cpu_measurements else 0.0
    max_cpu = max(cpu_measurements) if cpu_measurements else 0.0
    avg_mem = sum(mem_measurements) / len(mem_measurements) if mem_measurements else 0.0
    max_mem = max(mem_measurements) if mem_measurements else 0.0
    
    # Print results
    print("\n" + "="*90)
    print("LOCAL OLLAMA-ONLY BENCHMARK RESULTS")
    print("="*90)
    print(f"Total End-to-End Runtime: {total_elapsed:.2f} seconds")
    print(f"System CPU Usage:         Avg {avg_cpu:.1f}%, Max {max_cpu:.1f}%")
    print(f"System Memory Usage:      Avg {avg_mem:.1f}%, Max {max_mem:.1f}%")
    print("="*90)
    
    print("\nPer-Candidate Timing Breakdown:")
    print(f"{'Candidate':<15} | {'Status':<8} | {'Total Time':<10} | {'Intake':<8} | {'JD Parse':<8} | {'Assessors':<10} | {'Debate':<8} | {'Decider':<8}")
    print("-"*105)
    
    for r in sorted(results, key=lambda x: x["name"]):
        name = r["name"]
        if r["success"]:
            p = r["payload"]
            t = p.get("timings", {})
            print(f"{name:<15} | {'SUCCESS':<8} | {r['elapsed']:<10.2f}s | {t.get('intake', 0.0):<8.2f}s | {t.get('jd_parsing', 0.0):<8.2f}s | {t.get('assessors', 0.0):<10.2f}s | {t.get('debate', 0.0):<8.2f}s | {t.get('decider', 0.0):<8.2f}s")
        else:
            print(f"{name:<15} | {'FAILED':<8} | {r['elapsed']:<10.2f}s | N/A")
            
    print("="*105 + "\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
