"""
A container for storing and querying logs.
"""

import re
from itertools import groupby
from operator import attrgetter

from .result_entry import ResultEntry

__all__ = ["LogContainer"]


class LogContainer:
    """
    A container for storing and querying logs.
    """

    def __init__(self, entries: list[ResultEntry] = []) -> None:
        """
        Create log container.
        Entries are copied on construction.

        Parameters
        ----------
        entries : list[ResultEntry]
            List of ResultEntry objects.
        """
        self._logs = list(entries)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._logs):
            result = self._logs[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration()

    def __len__(self):
        """
        Get the number of ResultEntry messages in the container.
        """
        return len(self._logs)

    def __getitem__(self, subscript):
        """
        Get a ResultEntry message by index.
        """
        return self._logs[subscript]

    def contains_log(self, field: str, pattern: str) -> bool:
        """
        Check if a LogContainer contains a ResultEntry with the given field and pattern.
        """
        return any(log for log in self.get_logs_by_field(field, pattern))

    def contains_id(self, entry_id: str) -> bool:
        """
        Check if a ResultEntry with the given ID is contained in the container.
        """
        return any(log.id == entry_id for log in self._logs)

    def get_logs_by_field(self, field: str, pattern: str) -> "LogContainer":
        """
        Get all ResultEntry messages that match the given field and pattern.
        """
        regex = re.compile(pattern)
        entries = [log for log in self._logs if regex.search(getattr(log, field, ""))]
        return LogContainer(entries)

    def find_log(self, field: str, pattern: str) -> ResultEntry | None:
        """
        Find a ResultEntry message that matches the given field and pattern.
        Returns the first match or None if no match is found.
        Raises ValueError if multiple matches are found.
        """
        findings = self.get_logs_by_field(field, pattern)
        if len(findings) == 0:
            return None
        elif len(findings) == 1:
            return findings[0]
        elif len(findings) > 1:
            raise ValueError(f"Multiple logs found for {field=} and {pattern=}")

    def add_log(self, log: ResultEntry | list[ResultEntry]) -> None:
        """
        Add ResultEntry messages to the container.

        Parameters
        ----------
        log : ResultEntry | list[ResultEntry]
            Message or messages to add.
        """
        if isinstance(log, ResultEntry):
            self._logs.append(log)
        elif isinstance(log, list) and all([isinstance(x, ResultEntry) for x in log]):
            self._logs.extend(log)
        else:
            raise TypeError("log must be a ResultEntry or list[ResultEntry]")

    def get_logs(self) -> list[ResultEntry]:
        """
        Get all ResultEntry messages.
        """
        return self._logs[:]

    def clear_logs(self):
        """
        Clear all ResultEntry messages.
        """
        self._logs.clear()

    def remove_logs(self, field: str, pattern: str):
        """
        Remove all ResultEntry messages that match the given field and pattern.
        """
        regex = re.compile(pattern)
        self._logs = [log for log in self._logs if not regex.search(getattr(log, field, ""))]

    def group_by(self, attribute: str) -> dict[str, "LogContainer"]:
        """
        Group ResultEntry messages by a specified attribute.
        Returns a dictionary where the keys are the unique values of the attribute,
        and the values are LogContainer instances containing the grouped logs.
        """
        sorted_logs_by_attr = sorted(self._logs, key=attrgetter(attribute))
        grouped = groupby(sorted_logs_by_attr, key=attrgetter(attribute))
        return {key: LogContainer(list(group)) for key, group in grouped}
