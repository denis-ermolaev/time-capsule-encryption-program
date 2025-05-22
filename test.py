from typing import NotRequired, TypedDict

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
