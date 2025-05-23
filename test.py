from typing import NotRequired, TypedDict
from unittest.mock import Mock
from src.CapsuleProcessor import СapsuleProcessor


def some_condition():
    return True


x: str | None = "something" if some_condition() else None
if x is not None:
    # Mypy understands x won't be None here because of the if-statement
    print(x.upper())
# If you know a value can never be None due to some logic that mypy doesn't
# understand, use an assert
assert x is not None
print(x.upper())

mydict = TypedDict("mydict", {"1": int | None, "2": int, "3": NotRequired[int]})
a: mydict = {"1": 34, "2": 24}


assert "3" in a
assert a["1"] is not None
a["1"] += 5


a["3"] += 5
