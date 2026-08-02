import sys
sys.path.insert(0, ".")
import urllib3
import requests
import json
import time
from schemas import Module
from context import build_system_prompt, build_slide_prompt

urllib3.disable_warnings()

url = "https://stampede3.tacc.utexas.edu:60098/v1/chat/completions"
headers = {
    "Authorization": "Bearer flexserv",
    "x-flexserv-token": "flexserv",
    "x-flexserv-secret": "flexserv",
    "Content-Type": "application/json"
}

module = Module(
    id="pytorch-basics",
    title="pytorch basics",
    week=3,
    context="Basic PyTorch tensors and modules",
    difficulty="Intermediate"
)

prompt = build_slide_prompt(module)
system_prompt = build_system_prompt()

payload = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "stream": True,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 1024
}

print(f"Prompt length: {len(prompt)} chars")
print("Sending request with stream=True to measure TTFT (Time to First Token)...")
start_time = time.time()

try:
    response = requests.post(url, headers=headers, json=payload, verify=False, stream=True, timeout=120)
    print(f"Status Code: {response.status_code}")
    print(f"Time to headers: {time.time() - start_time:.2f}s")
    
    first_chunk = True
    for chunk in response.iter_lines():
        if chunk:
            if first_chunk:
                print(f"Time to first token chunk: {time.time() - start_time:.2f}s")
                first_chunk = False
            chunk_str = chunk.decode("utf-8")
            if "data: [DONE]" in chunk_str:
                break
            print(chunk_str[:120])
except Exception as e:
    print(f"Error: {e}")
