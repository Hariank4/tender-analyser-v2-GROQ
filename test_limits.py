import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "hi"}]
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
print("Status:", response.status_code)
for k, v in response.headers.items():
    if "ratelimit" in k.lower():
        print(f"{k}: {v}")

print("----------")
payload["model"] = "llama-3.3-70b-versatile"
response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
print("Status:", response.status_code)
for k, v in response.headers.items():
    if "ratelimit" in k.lower():
        print(f"{k}: {v}")
