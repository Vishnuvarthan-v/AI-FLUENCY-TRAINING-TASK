"""Day 6 task: Silver Oak Bookstore tools, with strict JSON Schemas."""
import ast
import operator

# Private bookstore data that no public LLM has ever seen
BOOKS = {
    "ALCH01": {"title": "The Alchemist", "price": 350, "stock": 40},
    "ATOM02": {"title": "Atomic Habits", "price": 450, "stock": 25},
    "SAPI03": {"title": "Sapiens", "price": 550, "stock": 10},
}
HARDCOVER_SURCHARGE = 200  # Rs. added to the paperback price


def get_book_price(book_code: str, edition: str = "paperback") -> str:
    """Return the price in rupees for ONE book code and edition."""
    book = BOOKS.get(book_code.strip().upper())
    if book is None:
        return (f"Unknown book code: {book_code}. "
                f"Valid codes: {', '.join(BOOKS)}")
    price = book["price"] + (HARDCOVER_SURCHARGE if edition == "hardcover" else 0)
    return str(price)


def get_book_stock(book_code: str) -> str:
    """Return the number of copies in stock for ONE book code."""
    book = BOOKS.get(book_code.strip().upper())
    if book is None:
        return (f"Unknown book code: {book_code}. "
                f"Valid codes: {', '.join(BOOKS)}")
    return str(book["stock"])


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg}


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression. Parses, never uses eval()."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}. Use only numbers and + - * / ( )."


TOOL_FUNCTIONS = {
    "get_book_price": get_book_price,
    "get_book_stock": get_book_stock,
    "calculator": calculator,
}

TOOLS = [
    {"type": "function", "function": {
        "name": "get_book_price",
        "description": ("Get the price in rupees of ONE book, for example ATOM02. "
                        "Returns the number only. Valid codes: ALCH01, ATOM02, SAPI03. "
                        "Edition is 'paperback' (default) or 'hardcover'."),
        "parameters": {
            "type": "object",
            "properties": {
                "book_code": {"type": "string",
                              "description": "Book code such as ATOM02"},
                "edition": {"type": "string", "enum": ["paperback", "hardcover"],
                            "description": "Edition; defaults to paperback"},
            },
            "required": ["book_code"],
            "additionalProperties": False,
        }}},
    {"type": "function", "function": {
        "name": "get_book_stock",
        "description": ("Get the number of copies in stock for ONE book code, "
                        "for example ATOM02. Returns the number only. "
                        "Valid codes: ALCH01, ATOM02, SAPI03."),
        "parameters": {
            "type": "object",
            "properties": {
                "book_code": {"type": "string",
                              "description": "Book code such as ATOM02"},
            },
            "required": ["book_code"],
            "additionalProperties": False,
        }}},
    {"type": "function", "function": {
        "name": "calculator",
        "description": ("Evaluate one arithmetic expression using + - * / and brackets, "
                        "for example (2 * 350 + 550) * 0.9. Returns the number only."),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string",
                               "description": "Arithmetic expression, digits and operators only"},
            },
            "required": ["expression"],
            "additionalProperties": False,
        }}},
]

# name -> the "parameters" block above: sent to the model AND used by validate.py
SCHEMAS = {t["function"]["name"]: t["function"]["parameters"] for t in TOOLS}