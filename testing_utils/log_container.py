"""
A container for storing and querying logs.
"""

__all__ = ["LogContainer"]

import re
from itertools import groupby
from operator import attrgetter
from typing import Any

from .result_entry import ResultEntry


class LogContainer:
    """
    A container for storing and querying logs.
    """

    def __init__(self, entries: list[ResultEntry] | None = None) -> None:
        """
        Create log container.
        Entries are copied on construction.

        Parameters
        ----------
        entries : list[ResultEntry] | None
            List of ResultEntry objects.
        """
        self._logs = list(entries or [])
        self._index = 0

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self._logs):
            result = self._logs[self._index]
            self._index += 1
            return result
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

    class _NotFound:
        """
        Internal type for failed search results.
        """

    _not_found = _NotFound()

    def _logs_by_field_str(self, field: str, pattern: str, excluded: bool) -> list[ResultEntry]:
        """
        Filter entries using regex matching.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : str
            Regex pattern to match.
        excluded : bool
            Return entries not matched.
        """
        entries = []
        regex = re.compile(pattern)
        for log in self._logs:
            found_value = getattr(log, field, self._not_found)
            if found_value == self._not_found:
                continue
            if not isinstance(found_value, type(pattern)):
                raise TypeError(
                    f"Type mismatch, provided value type: {type(pattern)}, found value type: {type(found_value)}"
                )
            found = regex.search(found_value) is not None
            if found ^ excluded:
                entries.append(log)
        return entries

    def _logs_by_field_any(self, field: str, pattern: Any, excluded: bool) -> list[ResultEntry]:
        """
        Filter entries by value.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : Any
            Pattern to match.
        excluded : bool
            Return entries not matched.
        """
        entries = []
        for log in self._logs:
            found_value = getattr(log, field, self._not_found)
            if found_value == self._not_found:
                continue
            if not isinstance(found_value, type(pattern)):
                raise TypeError(
                    f"Type mismatch, provided value type: {type(pattern)}, found value type: {type(found_value)}"
                )
            found = found_value == pattern
            if found ^ excluded:
                entries.append(log)
        return entries

    def _logs_by_field(self, field: str, pattern: Any, excluded: bool) -> list[ResultEntry]:
        """
        Filter entries by type specific filtering method.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : Any
            Pattern to match.
            Regex match is used for 'str' values.
        excluded : bool
            Return entries not matched.
        """

        if isinstance(pattern, str):
            return self._logs_by_field_str(field, pattern, excluded)
        else:
            return self._logs_by_field_any(field, pattern, excluded)

    def contains_log(self, field: str, pattern: Any) -> bool:
        """
        Check if a LogContainer contains a ResultEntry with the given field and pattern.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : Any
            Pattern to match.
            Regex match is used for 'str' values.
        """
        return len(self._logs_by_field(field, pattern, False)) > 0

    def contains_id(self, entry_id: str) -> bool:
        """
        Check if a ResultEntry with the given ID is contained in the container.
        """
        return any(log.id == entry_id for log in self._logs)

    def get_logs_by_field(self, field: str, pattern: Any) -> "LogContainer":
        """
        Get all ResultEntry messages that match the given field and pattern.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : Any
            Pattern to match.
            Regex match is used for 'str' values.
        """
        return LogContainer(self._logs_by_field(field, pattern, False))

    def find_log(self, field: str, pattern: Any) -> ResultEntry | None:
        """
        Find a ResultEntry message that matches the given field and pattern.
        Returns the first match or None if no match is found.
        Raises ValueError if multiple matches are found.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : Any
            Pattern to match.
            Regex match is used for 'str' values.
        """
        findings = self._logs_by_field(field, pattern, False)
        if len(findings) == 1:
            return findings[0]
        if len(findings) > 1:
            raise ValueError(f"Multiple logs found for {field=} and {pattern=}")

        return None

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
        elif isinstance(log, list) and all(isinstance(x, ResultEntry) for x in log):
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

    def remove_logs(self, field: str, pattern: Any):
        """
        Remove all ResultEntry messages that match the given field and pattern.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : Any
            Pattern to match.
            Regex match is used for 'str' values.
        """
        self._logs = self._logs_by_field(field, pattern, True)

    def group_by(self, attribute: str) -> dict[str, "LogContainer"]:
        """
        Group ResultEntry messages by a specified attribute.
        Returns a dictionary where the keys are the unique values of the attribute,
        and the values are LogContainer instances containing the grouped logs.
        """
        sorted_logs_by_attr = sorted(self._logs, key=attrgetter(attribute))
        grouped = groupby(sorted_logs_by_attr, key=attrgetter(attribute))
        return {key: LogContainer(list(group)) for key, group in grouped}
