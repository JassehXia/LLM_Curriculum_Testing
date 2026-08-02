import urllib3
import requests
import httpx
from openai import OpenAI

urllib3.disable_warnings()

BASE_URL = "https://stampede3.tacc.utexas.edu:60098/v1"
TOKEN = "flexserv"

def run_text_generation_test():
    print("=" * 60)
    print(f"Testing Text Generation API on FlexServ Port 60082")
    print("=" * 60)

    try:
        http_client = httpx.Client(
            timeout=httpx.Timeout(180.0, connect=30.0, read=180.0, write=30.0),
            verify=False
        )
        client = OpenAI(
            base_url=BASE_URL,
            api_key=TOKEN,
            timeout=180.0,
            default_headers={
                "x-flexserv-token": TOKEN,
                "x-flexserv-secret": TOKEN,
                "Authorization": f"Bearer {TOKEN}"
            },
            http_client=http_client
        )

        print("Sending prompt to Qwen/Qwen2.5-7B-Instruct...")
        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Confirm that text generation is working properly."}
            ],
            max_tokens=50
        )

        print("\n" + "=" * 60)
        print("SUCCESS! Model Output:")
        print("=" * 60)
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nAPI Completion Error: {e}")

if __name__ == "__main__":
    run_text_generation_test()
