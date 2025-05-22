from typing import NotRequired, TypedDict
from unittest.mock import Mock
from src.CapsuleProcessor import СapsuleProcessor

Point2D = TypedDict("Point2D", {"1": str, "2": str, "3": NotRequired[str]})

# a: Point2D = {"1": "3223", "2": "24546"}
a: Point2D = {"1": "3223", "2": "24546"}

a["3"] = str(0)
print(a)
c = ",".join([])
print(len(c), type(c))
# if "3" in a:
#     raise AssertionError("Ошибка")
# else:
#     a["3"] += "New Value"

# print(a)
attrs = {
    "id": 1,
    "read": False,
    "create": [
        "gfbgfb",
        "2025-04-26 14:00:00",
        "2025-04-26 14:00:00",
    ],
    "emergency": None,
    "opening_days_mode": None,
}
args = Mock(**attrs)
a = СapsuleProcessor(args, without_file=True)
print(a.final_console_output["encrypted_capsule"])


attrs = {
    "id": 1,
    "read": True,
    "create": None,
    "emergency": None,
    "opening_days_mode": None,
}
args = Mock(**attrs)
b = СapsuleProcessor(args, True, a.final_console_output["encrypted_capsule"])
print(b.final_console_output)
