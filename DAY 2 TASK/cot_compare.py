"""Day 2, Part C: Compare direct answers with answers that show concise reasoning."""

import sys
from pathlib import Path

# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# DAY 1 TASK contains config.py
DAY1_FOLDER = PROJECT_ROOT / "DAY 1 TASK"

# Allow Python to import config.py from DAY 1 TASK
sys.path.insert(0, str(DAY1_FOLDER))

from config import client, MODEL, banner


QUESTIONS = [
    # 1. Multi-step arithmetic
    (
        "Three books cost Rs. 350, Rs. 450, and Rs. 550. "
        "The store gives a 15% festival discount on the total, "
        "and the customer pays the discounted amount in 3 equal "
        "instalments. How much is each instalment?"
    ),

    # 2. Counting in two parts
    (
        "A bookstore has 24 shelves. Each shelf holds 15 fiction "
        "books and 10 non-fiction books. How many books are on "
        "all the shelves combined?"
    ),

    # 3. Ordering / logic
    (
        "The Alchemist sells more copies per week than Atomic Habits. "
        "Atomic Habits sells more copies than Sapiens. "
        "Sapiens sells more copies than a poetry collection. "
        "Which book sells the most, and which sells the least?"
    ),
]


DIRECT_PROMPT = (
    "You are a helpful assistant. "
    "Give only the final answer. Do not explain."
)


REASONING_PROMPT = (
    "You are a helpful assistant. "
    "Solve the problem using concise numbered steps. "
    "Show only the necessary calculations or reasoning, not private "
    "chain-of-thought. "
    "After the steps, write the last line exactly as: "
    "Final Answer: <answer>"
)


def ask(system_prompt, question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":

    banner("CHAIN-OF-THOUGHT COMPARISON")

    for number, question in enumerate(QUESTIONS, start=1):

        print("=" * 72)
        print(f"QUESTION {number}: {question}\n")

        print("--- WITHOUT CoT ---")
        print(ask(DIRECT_PROMPT, question))
        print()

        print("--- WITH REASONING ---")
        print(ask(REASONING_PROMPT, question))
        print()