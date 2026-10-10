
import time
import requests

BASE = "http://localhost:11434"

MODELS = ["qwen2.5:1.5b"]  # Add your second model here

PROMPTS = [
    "Reply with exactly: OK",
    "In two sentences, what is an AI agent?",
    "2 copies of The Alchemist at Rs. 350 and 1 copy of Sapiens at Rs. 550 get a "
    "10% book-fair discount. What is payable? Show the steps.",
    "What is the price of Atomic Habits (ATOM02) at Silver Oak Bookstore?"
]


def run(model, prompt):
    start = time.time()

    response = requests.post(
        f"{BASE}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=600
    )

    response.raise_for_status()
    data = response.json()

    elapsed = time.time() - start
    tokens = data.get("eval_count", 0)
    load_ms = data.get("load_duration", 0) / 1e6
    rate = tokens / elapsed if elapsed else 0

    return elapsed, tokens, rate, load_ms, data.get("response", "").strip()


if __name__ == "__main__":
    for model in MODELS:
        print("=" * 72)
        print("MODEL:", model)

        for prompt in PROMPTS:
            elapsed, tokens, rate, load_ms, text = run(model, prompt)

            print(f"\nPrompt: {prompt[:50]}")
            print(
                f"{elapsed:5.1f} s | {tokens:4d} tokens | "
                f"{rate:5.1f} tok/s | load {load_ms:7.1f} ms"
            )
            print(f"Answer: {text[:160]}")
        print()
