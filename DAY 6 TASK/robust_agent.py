"""Day 6 task: the bookstore agent on the OpenAI-compatible API, with validation and retry."""
import json
from config import client, MODEL, banner
from tools_v2 import TOOLS, TOOL_FUNCTIONS, SCHEMAS
from validate import validate_arguments

SYSTEM_PROMPT = (
    "You are a bookstore assistant for Silver Oak Bookstore. Never guess a price or "
    "stock figure: always call get_book_price or get_book_stock. Use calculator for "
    "every arithmetic step. Valid book codes: ALCH01 (The Alchemist), ATOM02 (Atomic "
    "Habits), SAPI03 (Sapiens). If no tool is needed, answer directly."
)

MAX_TOKENS = 500       # doubled automatically when a reply is truncated
TOKEN_CEILING = 2000
REPEAT_LIMIT = 3       # identical calls allowed before we stop


def handle_tool_call(call, log=True):
    """Run one tool call defensively. ALWAYS returns a string for the model."""
    name = call.function.name
    raw = call.function.arguments or "{}"

    # 1. the arguments are generated text: they may not be JSON at all
    try:
        arguments = json.loads(raw)
    except json.JSONDecodeError as error:
        return f"Argument error: invalid JSON ({error}). Send valid JSON for '{name}'."

    # 2. the tool may not exist
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return f"Unknown tool: {name}. Available tools: {', '.join(TOOL_FUNCTIONS)}."

    # 3. the arguments may not match the schema
    problem = validate_arguments(arguments, SCHEMAS[name])
    if problem:
        return f"Argument error: {problem}"

    # 4. the tool itself may fail
    try:
        result = str(function(**arguments))
    except Exception as error:
        result = f"Tool error in {name}: {type(error).__name__}: {error}"

    if log:
        print(f"    {name}({arguments}) -> {result[:100]}")
    return result


def agent(question, max_steps=6, verbose=True):
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]
    seen = {}
    max_tokens = MAX_TOKENS
    stats = {"steps": 0, "tool_calls": 0, "parallel": False, "truncated": False}

    for step in range(1, max_steps + 1):
        stats["steps"] = step
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS,
            temperature=0, max_tokens=max_tokens)
        choice = response.choices[0]
        message = choice.message

        # a truncated reply is a settings problem, not a model problem: retry bigger
        if choice.finish_reason == "length":
            stats["truncated"] = True
            if max_tokens >= TOKEN_CEILING:
                return f"Stopped: the reply was still truncated at {TOKEN_CEILING} tokens.", stats
            max_tokens *= 2
            if verbose:
                print(f"  step {step}: truncated, retrying with max_tokens={max_tokens}")
            continue

        # no tool calls: this is the final answer
        if not message.tool_calls:
            return (message.content or "").strip(), stats

        messages.append({
            "role": "assistant", "content": message.content or "",
            "tool_calls": [{"id": c.id, "type": "function",
                            "function": {"name": c.function.name,
                                         "arguments": c.function.arguments}}
                           for c in message.tool_calls]})

        n = len(message.tool_calls)
        stats["tool_calls"] += n
        stats["parallel"] = stats["parallel"] or n > 1
        if verbose:
            print(f"  step {step}: {n} tool call(s)")

        # ALWAYS loop: there may be several calls, and each id needs its own answer
        for call in message.tool_calls:
            signature = (call.function.name, call.function.arguments)
            seen[signature] = seen.get(signature, 0) + 1
            if seen[signature] >= REPEAT_LIMIT:
                return (f"Stopped: {call.function.name} was called {REPEAT_LIMIT} times "
                        f"with the same arguments and made no progress."), stats
            result = handle_tool_call(call, log=verbose)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    return "Stopped: maximum steps reached without a final answer.", stats


QUESTIONS = [
    ("single tool",
     "What is the price of Atomic Habits (ATOM02)?"),
    ("two tools at once",
     "What is the total cost of 2 copies of The Alchemist (ALCH01) and 1 copy of Sapiens (SAPI03)?"),
    ("compare stock (parallel + calculator)",
     "Is the stock of The Alchemist (ALCH01) more than Sapiens (SAPI03), and by how much?"),
    ("tempts an invalid value",
     "What is the price of the signed collector's edition of Sapiens (SAPI03)?"),
    ("unknown book code",
     "What is the price of the book with code ZZZZ99?"),
    ("no tool needed",
     "Write a two-line message announcing a weekend book fair discount."),
]

if __name__ == "__main__":
    banner("ROBUST AGENT (Silver Oak Bookstore)")
    for label, question in QUESTIONS:
        print(f"\n[{label}]\nQ: {question}")
        answer, stats = agent(question)
        print("A:", answer)
        print(f"   steps={stats['steps']} tool_calls={stats['tool_calls']} "
              f"parallel={stats['parallel']} truncated={stats['truncated']}")