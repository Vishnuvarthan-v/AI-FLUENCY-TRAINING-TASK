"""Day 6 task: check tool arguments against the JSON Schema before calling the function."""

TYPES = {"string": str, "number": (int, float), "integer": int,
         "boolean": bool, "array": list, "object": dict}


def validate_arguments(arguments, schema):
    """Return None when valid, or a message saying what was wrong AND what was expected."""
    if not isinstance(arguments, dict):
        return (f"Arguments must be a JSON object, but got "
                f"{type(arguments).__name__}: {arguments!r}.")
    properties = schema.get("properties", {})

    for name in schema.get("required", []):                    # 1. missing required
        if name not in arguments:
            return (f"Missing required argument '{name}'. "
                    f"Expected: {', '.join(properties)}.")

    if schema.get("additionalProperties") is False:            # 2. invented extras
        extra = [k for k in arguments if k not in properties]
        if extra:
            return (f"Unexpected argument(s): {', '.join(extra)}. "
                    f"Allowed: {', '.join(properties)}.")

    for name, value in arguments.items():                      # 3. types and enums
        rule = properties.get(name, {})
        expected = TYPES.get(rule.get("type"))
        # bool is a subclass of int in Python, so True must not pass as a number
        is_bool_as_number = isinstance(value, bool) and rule.get("type") in ("number", "integer")
        if expected and (not isinstance(value, expected) or is_bool_as_number):
            return (f"Argument '{name}' must be a {rule['type']}, "
                    f"but got {type(value).__name__}: {value!r}.")
        if "enum" in rule and value not in rule["enum"]:                  # 4. outside enum
            return f"Argument '{name}' must be one of {rule['enum']}, got {value!r}."
    return None


if __name__ == "__main__":
    from tools_v2 import SCHEMAS
    schema = SCHEMAS["get_book_price"]
    cases = [
        {"book_code": "ATOM02"},
        {"book_code": "ATOM02", "edition": "hardcover"},
        {},
        {"book_code": 450},
        {"book_code": "ATOM02", "edition": "signed"},
        {"book_code": "ATOM02", "discount": 10},
    ]
    for case in cases:
        print(f"{str(case):<52} -> {validate_arguments(case, schema) or 'OK'}")