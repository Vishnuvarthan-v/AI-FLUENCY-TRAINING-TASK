"""Day 2: Print the agent's real ReAct trace."""

import sys
from pathlib import Path


# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Find DAY 1 TASK folder
DAY1_FOLDER = PROJECT_ROOT / "DAY 1 TASK"

# Allow Python to import agent.py from DAY 1 TASK
sys.path.insert(0, str(DAY1_FOLDER))


# Import the agent from DAY 1 TASK
from agent import agent


QUESTION = (
    "Which is cheaper: 2 copies of The Alchemist (ALCH01) and "
    "1 copy of Atomic Habits (ATOM02) with a 10% festival discount, "
    "or one copy each of all three books (ALCH01, ATOM02, SAPI03) "
    "with a 20% festival discount? By how much?"
)


print("QUESTION:", QUESTION)
print("\n--- the agent's actions and observations ---")

answer = agent(QUESTION, max_steps=8)

print("\nFINAL ANSWER:", answer)