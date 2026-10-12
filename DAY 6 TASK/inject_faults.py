"""Day 6 task: prove the guards work, without needing the model to misbehave."""
import json
from robust_agent import handle_tool_call


class FakeFunction:
    def __init__(self, name, arguments):
        self.name, self.arguments = name, arguments


class FakeCall:
    """Looks exactly like one entry of message.tool_calls."""
    def __init__(self, name, arguments, call_id="call_test"):
        self.id, self.type = call_id, "function"
        self.function = FakeFunction(name, arguments)


FAULTS = [
    ("a good call",             FakeCall("get_book_price", '{"book_code": "ATOM02"}')),
    ("invalid JSON",            FakeCall("get_book_price", '{"book_code": "ATOM02"')),
    ("unknown tool",            FakeCall("send_email", '{"to": "buyer@silveroak.in"}')),
    ("missing required",        FakeCall("get_book_price", '{}')),
    ("wrong type",              FakeCall("get_book_price", '{"book_code": 450}')),
    ("value outside the enum",  FakeCall("get_book_price",
                                         '{"book_code": "SAPI03", "edition": "signed"}')),
    ("invented extra argument", FakeCall("get_book_stock",
                                         '{"book_code": "SAPI03", "branch": "campus"}')),
    ("unknown book code",       FakeCall("get_book_stock", '{"book_code": "ZZZZ99"}')),
    ("unsafe expression",       FakeCall("calculator",
                                         json.dumps({"expression": "__import__('os').system('ls')"}))),
    ("empty arguments string",  FakeCall("calculator", '')),
    # --- two faults of my own design ---
    ("OWN 1: wrong capitalisation", FakeCall("Get_Book_Price", '{"book_code": "ATOM02"}')),
    ("OWN 2: array, not object",    FakeCall("get_book_price", '["ATOM02", "hardcover"]')),
]

if __name__ == "__main__":
    print("=" * 90)
    for label, call in FAULTS:
        result = handle_tool_call(call, log=False)
        print(f"{label:<30} -> {result[:80]}")
    print("=" * 90)
    print("Every line above is a STRING. Nothing raised, nothing crashed:")
    print("each message goes back to the model, which can try again.")