import os
import requests

VLLM_URL = os.getenv("VLLM_URL", "http://127.0.0.1:8000/generate")
VLLM_API_KEY = os.getenv("VLLM_API_KEY")  # optional

def test_vllm():
    headers = {"Content-Type": "application/json"}
    if VLLM_API_KEY:
        headers["Authorization"] = f"Bearer {VLLM_API_KEY}"

    payload = {
        "model": "google/gemma-3-270m",
        "prompt": "You are a helpful assistant.\nUser: Hello, can you respond?\nAssistant:\n",
        "max_output_tokens": 100,   # vLLM uses max_output_tokens instead of max_tokens
        "temperature": 0.7,
    }

    try:
        resp = requests.post(VLLM_URL, json=payload, headers=headers, timeout=30)

        # DEBUG prints to check the raw response
        print("Status code:", resp.status_code)
        print("Response body:", resp.text)

        resp.raise_for_status()
        data = resp.json()
        # vLLM returns 'response' for simple generate
        answer = data.get("response", "")
        print("vLLM response:", answer)
    except Exception as e:
        print("Error contacting vLLM server:", e)


if __name__ == "__main__":
    test_vllm()
