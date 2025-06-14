import re
from typing import Generator

from .result_entry import ResultEntry

__all__ = ["LogContainer"]


class LogContainer:
    """
    A container for ResultEntry messages.
    """

    def __init__(self):
        self.logs = []

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.logs):
            result = self.logs[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration()

    def __len__(self):
        """
        Get the number of ResultEntry messages in the container.
        """
        return len(self.logs)

    def __getitem__(self, subscript):
        """
        Get a ResultEntry message by index.
        """
        return self.logs[subscript]

    @classmethod
    def from_entries(cls, entries: list[ResultEntry]) -> "LogContainer":
        """
        Create a LogContainer from a list of ResultEntry messages.
        """
        if not all(isinstance(entry, ResultEntry) for entry in entries):
            raise TypeError("All entries must be instances of ResultEntry")
        container = cls()
        container.logs.extend(entries)
        return container

    def contains_log(self, field: str, pattern: str) -> bool:
        """
        Check if a LogContainer contains a ResultEntry with the given field and pattern.
        """
        return any(log for log in self.get_logs_by_field(field, pattern))

    def contains_id(self, entry_id: str) -> bool:
        """
        Check if a ResultEntry with the given ID is contained in the container.
        """
        return any(log.id == entry_id for log in self.logs)

    def get_logs_by_field(self, field: str, pattern: str) -> Generator[ResultEntry, None, None]:
        """
        Get all ResultEntry messages that match the given field and pattern.
        """
        regex = re.compile(pattern)
        for log in self.logs:
            if regex.search(getattr(log, field, "")):
                yield log

    def find_log(self, field: str, pattern: str) -> ResultEntry | None:
        """
        Find a ResultEntry message that matches the given field and pattern.
        Returns the first match or None if no match is found.
        Raises ValueError if multiple matches are found.
        """
        [*findings] = self.get_logs_by_field(field, pattern)
        if len(findings) == 0:
            return None
        elif len(findings) == 1:
            return findings[0]
        elif len(findings) > 1:
            raise ValueError(f"Multiple logs found for {field=} and {pattern=}")

    def add_log(self, log: ResultEntry):
        """
        Add a ResultEntry message to the container.
        """
        if not isinstance(log, ResultEntry):
            raise TypeError("log must be an instance of ResultEntry")
        self.logs.append(log)

    def get_logs(self) -> list[ResultEntry]:
        """
        Get all ResultEntry messages.
        """
        return self.logs[:]

    def clear_logs(self):
        """
        Clear all ResultEntry messages.
        """
        self.logs.clear()

    def remove_logs(self, field: str, pattern: str):
        """
        Remove all ResultEntry messages that match the given field and pattern.
        """
        regex = re.compile(pattern)
        self.logs = [log for log in self.logs if not regex.search(getattr(log, field, ""))]
