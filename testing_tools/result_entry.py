"""
Structured representation of test log entries.
"""

import re
from typing import Any


class ResultEntry:
    """
    Structured representation of test log entries.
    """

    def __init__(self, json_message: dict[str, Any]) -> None:
        for key in json_message:
            if key == "fields":
                for inner_key in json_message[key]:
                    self._add_attribute(inner_key, json_message[key][inner_key])
            else:
                self._add_attribute(key, json_message[key])

    def _camel_case_to_snake_case(self, name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def _add_attribute(self, name: str, value: Any) -> None:
        name = self._camel_case_to_snake_case(name)
        if hasattr(self, name):
            raise RuntimeError(f"Tries to add duplicated field {name} to the ResultEntry, test issue!")
        setattr(self, name, value)

    def __str__(self) -> str:
        members = [f"{attr}={getattr(self, attr)}" for attr in vars(self)]
        return f"ResultEntry({', '.join(members)})"
