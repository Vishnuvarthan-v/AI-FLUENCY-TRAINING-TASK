"""Day 6 task: force the model to answer in a fixed JSON shape instead of free text."""
import json
from config import client, MODEL, banner

SCHEMA = {
    "type": "object",
    "properties": {
        "book_code": {"type": "string", "enum": ["ALCH01", "ATOM02", "SAPI03"]},
        "quantity": {"type": "integer"},
        "edition": {"type": "string", "enum": ["paperback", "hardcover"]},
        "needs_stock_check": {"type": "boolean"},
    },
    "required": ["book_code", "quantity", "edition", "needs_stock_check"],
    "additionalProperties": False,
}

QUESTION = ("I would like 3 hardcover copies of Sapiens for the book club. "
            "Please check that you have enough in stock.")

SYSTEM = ("Extract the customer's request as JSON with keys book_code, quantity, "
          "edition and needs_stock_check. Book codes: ALCH01 (The Alchemist), "
          "ATOM02 (Atomic Habits), SAPI03 (Sapiens). Reply with JSON only.")


def ask(response_format, label):
    print(f"\n--- {label} ---")
    try:
        kwargs = {"response_format": response_format} if response_format else {}
        reply = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": QUESTION}],
            temperature=0, **kwargs)
        text = reply.choices[0].message.content.strip()
        print("raw   :", text)
        parsed = json.loads(text)
        print("parsed:", parsed)
        missing = [k for k in SCHEMA["required"] if k not in parsed]
        extra = [k for k in parsed if k not in SCHEMA["properties"]]
        print("shape :", "matches my schema" if not missing and not extra
              else f"WRONG SHAPE (missing={missing}, extra={extra})")
    except Exception as error:
        print(f"not supported here / failed ({type(error).__name__}: {error})")


if __name__ == "__main__":
    banner("STRUCTURED OUTPUTS (Silver Oak Bookstore)")
    ask(None, "1. no constraint (free text)")
    ask({"type": "json_object"}, "2. JSON mode: valid JSON, any shape")
    ask({"type": "json_schema",
         "json_schema": {"name": "book_order", "schema": SCHEMA, "strict": True}},
        "3. schema mode: valid JSON in MY shape")