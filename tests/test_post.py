import requests

url = "http://localhost:8000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}

payload = {
    "model": "Qwen/Qwen2.5-Coder-32B-Instruct",
    "messages": [
        {"role": "user", "content": "Hello! Confirm connection."}
    ],
    "max_tokens": 50
}

try:
    print(f"Sending POST request to local vLLM endpoint ({url})...")
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:\n{response.text}")
except Exception as e:
    print(f"Error: {e}")
