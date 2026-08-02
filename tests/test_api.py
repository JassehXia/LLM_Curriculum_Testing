import urllib3
import requests
import httpx
from openai import OpenAI

# Suppress SSL verification warnings for custom HPC cluster ports
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target Endpoint URL & Authentication Token
BASE_URL = "http://localhost:8000/v1"
TOKEN = "none"

# Headers for REST & FlexServ Auth
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "x-flexserv-token": TOKEN,
    "x-flexserv-secret": TOKEN
}

def test_raw_rest_api():
    """Test standard REST HTTP requests to models endpoint."""
    print("=" * 60)
    print(f"1. Testing REST HTTP GET request to: {BASE_URL}/models")
    print("=" * 60)
    
    models_url = f"{BASE_URL}/models"
    try:
        # verify=False handles custom/self-signed SSL certificates on TACC cluster ports
        response = requests.get(models_url, headers=HEADERS, verify=False, timeout=10)
        print(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Successfully connected to endpoint!")
            print("Response JSON:")
            print(response.json())
        else:
            print(f"Response Error Body: {response.text}")
    except Exception as e:
        print(f"Failed to connect to REST endpoint: {e}")

def test_openai_client():
    """Test OpenAI SDK client against the vLLM / FlexServ endpoint."""
    print("\n" + "=" * 60)
    print(f"2. Testing OpenAI Python Client targeting: {BASE_URL}")
    print("=" * 60)

    try:
        # Use httpx.Client with verify=False for OpenAI SDK
        custom_http_client = httpx.Client(verify=False)

        client = OpenAI(
            base_url=BASE_URL,
            api_key=TOKEN,
            default_headers={"x-flexserv-token": TOKEN},
            http_client=custom_http_client
        )

        print("Sending chat completion request...")
        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": "Hello! Confirm that you are online and responding properly."}
            ],
            max_tokens=2048,
            temperature=.2
        )
        print("Success! Response from model:")
        print(completion.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI Client Error: {e}")

if __name__ == "__main__":
    test_raw_rest_api()
    test_openai_client()
