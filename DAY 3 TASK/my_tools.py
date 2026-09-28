"""Day 3: tools for the bookstore agent you build yourself."""

import ast
import operator
import os
import re


# ---------- Tool 1: a safe calculator ----------

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg
}


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](
            _evaluate(node.left),
            _evaluate(node.right)
        )

    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](
            _evaluate(node.operand)
        )

    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression such as (650 + 850) * 0.9."""

    try:
        return str(
            _evaluate(
                ast.parse(expression, mode="eval").body
            )
        )

    except Exception as error:
        return (
            f"Calculator error: {error}. "
            "Use only numbers and + - * / ( )."
        )


# ---------- Tool 2: a web page reader ----------

TAG = re.compile(
    r"<(script|style)[^>]*>.*?</\1>|<[^>]+>",
    re.S | re.I
)

SPACES = re.compile(r"\s+")


def read_webpage(url: str, max_chars: int = 2000) -> str:
    """Fetch a web page or local HTML/text file and return readable text."""

    try:

        # Read a real website
        if url.startswith("http://") or url.startswith("https://"):

            import requests

            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "AgenticAI-Lab/1.0"}
            )

            response.raise_for_status()

            raw = response.text

        # Read a local file
        elif os.path.exists(url):

            if not url.lower().endswith(
                (".html", ".htm", ".txt")
            ):
                return (
                    "Read error: only .html, .htm and .txt "
                    "files can be read."
                )

            with open(
                url,
                encoding="utf-8",
                errors="ignore"
            ) as file:

                raw = file.read()

        # File does not exist
        else:

            return (
                f"Read error: '{url}' is not a URL "
                "and no such file exists."
            )

    except Exception as error:

        return (
            f"Read error: {type(error).__name__}: {error}"
        )

    # Remove HTML tags, script and style content
    text = SPACES.sub(
        " ",
        TAG.sub(" ", raw)
    ).strip()

    # Prevent context overflow
    if len(text) > max_chars:

        text = (
            text[:max_chars]
            + f" ... [truncated, {len(text)} characters total]"
        )

    return text or "Read error: the page contained no readable text."


# ---------- Tool Registry ----------

TOOL_FUNCTIONS = {
    "calculator": calculator,
    "read_webpage": read_webpage
}


# ---------- JSON Tool Schemas ----------

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description":
                "Evaluate an arithmetic expression using "
                "+ - * / and brackets, for example "
                "(650 + 850) * 0.9.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description":
                            "The arithmetic expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description":
                "Read a web page or a local HTML/text file "
                "and return its visible text. Give a full URL "
                "such as https://example.com or a file name "
                "such as books.html.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description":
                            "URL or local file name to read"
                    }
                },
                "required": ["url"]
            }
        }
    }

]


# ---------- Direct Testing ----------

if __name__ == "__main__":

    print(calculator("(650 + 850) * 0.9"))

    print(calculator("950 + 750 + 650"))

    print(calculator("15 * 950 / 100"))

    print(calculator("import os"))

    print(read_webpage("books.html")[:200])

    print(read_webpage("missing_book.html"))