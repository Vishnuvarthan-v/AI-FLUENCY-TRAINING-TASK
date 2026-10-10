
import json
import time
import requests

BASE = "http://localhost:11434"
MODEL = "qwen2.5:1.5b"
PROMPT = "In three sentences, explain what an AI agent is."


def list_models():
    """GET /api/tags - list models stored on disk."""
    response = requests.get(f"{BASE}/api/tags", timeout=30)
    response.raise_for_status()

    tags = response.json()

    print("Models on disk:")
    for model in tags.get("models", []):
        print(
            f" {model['name']:<28} "
            f"{model.get('size', 0) / 1e9:5.2f} GB"
        )


def loaded_models():
    """GET /api/ps - list models currently loaded in memory."""
    response = requests.get(f"{BASE}/api/ps", timeout=30)
    response.raise_for_status()

    running = response.json().get("models", [])

    if not running:
        print("Nothing is loaded in memory.")
        return

    for model in running:
        print(
            f"Loaded: {model['name']} "
            f"{model.get('size', 0) / 1e9:5.2f} GB"
        )


def generate_once(model=MODEL, prompt=PROMPT):
    """POST /api/generate - generate one complete response."""
    start = time.time()

    response = requests.post(
        f"{BASE}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=300
    )

    response.raise_for_status()
    data = response.json()

    elapsed = time.time() - start
    tokens = data.get("eval_count", 0)
    speed = tokens / elapsed if elapsed else 0

    print(
        f"\n[generate] {elapsed:.1f} s for {tokens} tokens "
        f"({speed:.1f} tokens/s)"
    )
    print(data.get("response", "").strip()[:300])


def chat_streaming(model=MODEL, prompt=PROMPT):
    """POST /api/chat - measure time to first generated content."""
    start = time.time()
    first_token_at = None
    pieces = []

    with requests.post(
        f"{BASE}/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": True
        },
        stream=True,
        timeout=300
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            chunk = json.loads(line)
            piece = chunk.get("message", {}).get("content", "")

            if piece and first_token_at is None:
                first_token_at = time.time() - start

            pieces.append(piece)

    total = time.time() - start
    text = "".join(pieces)

    ttft = first_token_at if first_token_at is not None else total

    print(
        f"\n[chat, streaming] TTFT {ttft:.2f} s "
        f"| total {total:.1f} s "
        f"| {len(text)} characters"
    )
    print(text.strip()[:300])


def openai_compatible(model=MODEL, prompt=PROMPT):
    """POST /v1/chat/completions - test OpenAI-compatible access."""
    response = requests.post(
        f"{BASE}/v1/chat/completions",
        headers={"Authorization": "Bearer ollama"},
        json={
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        },
        timeout=300
    )

    response.raise_for_status()
    data = response.json()

    print("\n[/v1/chat/completions]")
    print(data["choices"][0]["message"]["content"].strip()[:300])


if __name__ == "__main__":
    try:
        list_models()
        loaded_models()
        generate_once()
        chat_streaming()
        openai_compatible()

    except requests.exceptions.ConnectionError:
        print(
            "\nERROR: Cannot connect to Ollama. "
            "Check whether Ollama is running."
        )

    except requests.exceptions.RequestException as error:
        print(f"\nAPI request failed: {error}")

    print("\nPart C testing completed.")
