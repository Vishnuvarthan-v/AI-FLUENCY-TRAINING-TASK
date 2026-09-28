"""Day 3: a ReAct agent from scratch."""

import json

from config import client, MODEL, banner
from my_tools import TOOLS, TOOL_FUNCTIONS


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = (
    "You are a bookstore assistant. Use read_webpage to read any bookstore page "
    "or file the user mentions, and use calculator for every arithmetic step. "
    "Never guess a price that should come from the bookstore page. "
    "If no tool is needed, answer directly."
)


# ============================================================
# REACT AGENT
# ============================================================

def agent(question, max_steps=6, verbose=True):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for step in range(1, max_steps + 1):

        # ----------------------------------------------------
        # 1. REASON
        # ----------------------------------------------------

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0
        )

        message = response.choices[0].message

        # ----------------------------------------------------
        # 2. STOP IF NO TOOL IS REQUESTED
        # ----------------------------------------------------

        if not message.tool_calls:
            return message.content.strip()

        # ----------------------------------------------------
        # 3. RECORD THE MODEL'S TOOL REQUEST
        # ----------------------------------------------------

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                }
                for call in message.tool_calls
            ]
        })

        # ----------------------------------------------------
        # 4. ACT AND 5. OBSERVE
        # ----------------------------------------------------

        for call in message.tool_calls:

            name = call.function.name
            arguments = {}

            try:

                arguments = json.loads(
                    call.function.arguments or "{}"
                )

                # SAFE TOOL LOOKUP
                function = TOOL_FUNCTIONS.get(name)

                # ------------------------------------------------
                # UNKNOWN TOOL
                # ------------------------------------------------

                if function is None:

                    result = (
                        f"Unknown tool: {name}. "
                        f"Available: {list(TOOL_FUNCTIONS)}"
                    )

                # ------------------------------------------------
                # VALID TOOL
                # ------------------------------------------------

                else:

                    result = function(**arguments)

            # ----------------------------------------------------
            # INVALID JSON
            # ----------------------------------------------------

            except json.JSONDecodeError as error:

                result = (
                    f"Argument error: {error}. "
                    "Send valid JSON."
                )

            # ----------------------------------------------------
            # WRONG ARGUMENTS
            # ----------------------------------------------------

            except TypeError as error:

                result = f"Argument error: {error}"

            # ----------------------------------------------------
            # OTHER TOOL ERRORS
            # ----------------------------------------------------

            except Exception as error:

                result = (
                    f"Tool error: "
                    f"{type(error).__name__}: {error}"
                )

            # ----------------------------------------------------
            # PRINT TRACE
            # ----------------------------------------------------

            if verbose:

                print(
                    f"  step {step}: "
                    f"{name}({arguments}) -> "
                    f"{str(result)[:120]}"
                )

            # ----------------------------------------------------
            # SEND OBSERVATION BACK TO MODEL
            # ----------------------------------------------------

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            })

    # ------------------------------------------------------------
    # SAFETY EXIT
    # ------------------------------------------------------------

    return "Stopped: maximum steps reached without a final answer."


# ============================================================
# QUESTION B
# ============================================================

questions = [

    (
        "Read books.html and tell me the total price of "
        "Python Programming and Machine Learning Basics "
        "after the 10 percent student discount."
    ),

    (
        "Read missing_book.html and tell me the price "
        "of Java Programming."
    ),

    (
        "Read big_books.html and tell me how many "
        "books are listed."
    )
]


# ============================================================
# RUN THE TEST
# ============================================================

if __name__ == "__main__":

    banner("MY AGENT - SAFE TOOL LOOKUP")

    print()
    print("=" * 70)
    print("QUESTION B")
    print("=" * 70)

    print()
    print("Q:", question)
    print()

    answer = agent(question)

    print()
    print("A:", answer)
    print()