"""Day 3: ReAct agent with guards."""

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
# GUARDS
# ============================================================

MAX_TOOL_CHARS = 1500
# Guard 2: no single observation may be larger than this

CHAR_BUDGET = 30000
# Guard 3: total characters sent to the model in one run


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

    # Guard 1: repeat detection
    seen_calls = {}

    # Guard 3: character budget
    chars_sent = 0

    for step in range(1, max_steps + 1):

        # ----------------------------------------------------
        # GUARD 3: CHARACTER BUDGET
        # ----------------------------------------------------

        chars_sent += sum(
            len(str(m.get("content", "")))
            for m in messages
        )

        if chars_sent > CHAR_BUDGET:

            return (
                f"Stopped: character budget exceeded "
                f"({chars_sent} sent)."
            )

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
        # 3. RECORD MODEL TOOL REQUEST
        # ----------------------------------------------------

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {
                        "name": c.function.name,
                        "arguments": c.function.arguments
                    }
                }
                for c in message.tool_calls
            ]
        })

        # ----------------------------------------------------
        # 4. ACT
        # 5. OBSERVE
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

                if function is None:

                    result = (
                        f"Unknown tool: {name}. "
                        f"Available: {list(TOOL_FUNCTIONS)}"
                    )

                else:

                    result = function(**arguments)

            # ------------------------------------------------
            # INVALID JSON
            # ------------------------------------------------

            except json.JSONDecodeError as error:

                result = (
                    f"Argument error: {error}. "
                    "Send valid JSON."
                )

            # ------------------------------------------------
            # WRONG ARGUMENTS
            # ------------------------------------------------

            except TypeError as error:

                result = f"Argument error: {error}"

            # ------------------------------------------------
            # CONVERT RESULT TO STRING
            # ------------------------------------------------

            result = str(result)

            # ------------------------------------------------
            # GUARD 1: REPEAT DETECTION
            # ------------------------------------------------

            signature = (
                name,
                json.dumps(
                    arguments,
                    sort_keys=True
                )
            )

            seen_calls[signature] = (
                seen_calls.get(signature, 0) + 1
            )

            if seen_calls[signature] >= 3:

                return (
                    f"Stopped: the tool {name} was called "
                    f"3 times with the same arguments and "
                    f"no progress was made. "
                    f"Last result: {result[:200]}"
                )

            # ------------------------------------------------
            # GUARD 2: OBSERVATION TRUNCATION
            # ------------------------------------------------

            if len(result) > MAX_TOOL_CHARS:

                result = (
                    result[:MAX_TOOL_CHARS]
                    + " ... [observation truncated]"
                )

            # ------------------------------------------------
            # PRINT TRACE
            # ------------------------------------------------

            if verbose:

                print(
                    f"  step {step}: "
                    f"{name}({arguments}) -> "
                    f"{result[:120]}"
                )

            # ------------------------------------------------
            # SEND OBSERVATION BACK TO MODEL
            # ------------------------------------------------

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })

    # --------------------------------------------------------
    # SAFETY EXIT
    # --------------------------------------------------------

    return "Stopped: maximum steps reached without a final answer."


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":

    banner("MY AGENT (guards on)")

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

    for question in questions:

        print()
        print("=" * 70)
        print("QUESTION")
        print("=" * 70)

        print()
        print("Q:", question)
        print()

        print("A:", agent(question))