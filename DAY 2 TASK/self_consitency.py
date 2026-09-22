"""Day 2, Part D: Run the same reasoning prompt several times
and take the majority answer.
"""

import sys
from pathlib import Path
from collections import Counter


# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# config.py is inside DAY 1 TASK
DAY1_FOLDER = PROJECT_ROOT / "DAY 1 TASK"

# Allow Python to import files from DAY 1 TASK
sys.path.insert(0, str(DAY1_FOLDER))


# Import configuration
from config import client, MODEL, banner

# Import the prompt and questions from cot_compare.py
from cot_compare import REASONING_PROMPT, QUESTIONS


RUNS = 5

# Use a non-zero temperature so different runs may produce
# slightly different responses.
TEMPERATURE = 0.8


def final_answer(text):
    """Extract the answer after 'Final Answer:'."""

    for line in reversed(text.splitlines()):

        if "final answer" in line.lower():

            return line.split(":", 1)[-1].strip()

    if text.strip():

        return text.splitlines()[-1].strip()

    return "(empty)"


def run_many(question, runs=RUNS, temperature=TEMPERATURE):

    answers = []

    for attempt in range(1, runs + 1):

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": REASONING_PROMPT
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=temperature,
        )

        answer = final_answer(
            response.choices[0].message.content
        )

        print(f"Run {attempt}: {answer}")

        answers.append(answer)

    return answers


if __name__ == "__main__":

    banner("SELF-CONSISTENCY")

    # Use the first question from cot_compare.py
    question = QUESTIONS[0]

    print("QUESTION:", question)
    print()

    answers = run_many(question)

    winner, count = Counter(answers).most_common(1)[0]

    print(
        f"\nMajority answer ({count} of {len(answers)} runs): {winner}"
    )