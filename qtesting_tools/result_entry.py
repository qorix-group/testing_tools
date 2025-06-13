from datetime import datetime
from typing import Dict


class ResultEntry:
    def __init__(self, json_message: Dict):
        self.timestamp = datetime.fromisoformat(json_message.get("timestamp"))
        self.target = json_message.get("target")
        self.level = json_message.get("level")
        self.thread_id = json_message.get("threadId")

    def __str__(self) -> str:
        return f"ResultEntry(timestamp={self.timestamp}, target={self.target}, level={self.level}, thread_id={self.thread_id})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ResultEntry):
            return NotImplemented
        return self.timestamp == other.timestamp

    def __lt__(self, other) -> bool:
        if not isinstance(other, ResultEntry):
            return NotImplemented
        return self.timestamp < other.timestamp

    def __gt__(self, other) -> bool:
        if not isinstance(other, ResultEntry):
            return NotImplemented
        return self.timestamp > other.timestamp


class ResultRuntime(ResultEntry):
    def __init__(self, json_message: Dict):
        super().__init__(json_message)
        self.id = json_message.get("fields").get("id")
        self.location = json_message.get("fields").get("location")
        self.message = json_message.get("fields").get("message")

    def __str__(self) -> str:
        return f"ResultRuntime(timestamp={self.timestamp}, target={self.target}, level={self.level}, thread_id={self.thread_id}, id={self.id}, location={self.location}, message={self.message})"


class ResultOrchestration(ResultEntry):
    def __init__(self, json_message: Dict):
        super().__init__(json_message)
        self.message = json_message.get("fields").get("message")

    def __str__(self) -> str:
        return f"ResultOrchestration(timestamp={self.timestamp}, target={self.target}, level={self.level}, thread_id={self.thread_id}, message={self.message})"
