import re
from datetime import datetime
from typing import Dict


class ResultEntry:
    def __init__(self, json_message: Dict):
        for key in json_message:
            if key == "timestamp":
                self._add_attribute(key, datetime.fromisoformat(json_message[key]))
            elif key == "fields":
                for inner_key in json_message[key]:
                    self._add_attribute(inner_key, json_message[key][inner_key])
            else:
                self._add_attribute(key, json_message[key])

    def _camel_case_to_snake_case(self, name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def _add_attribute(self, name: str, value: any) -> None:
        name = self._camel_case_to_snake_case(name)
        if hasattr(self, name):
            raise RuntimeError(f"Tries to add duplicated field {name} to the ResultEntry, test issue!")
        else:
            setattr(self, name, value)

    def __str__(self) -> str:
        members = [f"{attr}={getattr(self, attr)}" for attr in vars(self)]
        return f"ResultEntry({', '.join(members)})"
