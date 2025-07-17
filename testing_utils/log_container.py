"""
A container for storing and querying logs.
"""

__all__ = ["LogContainer"]

import re
from itertools import groupby
from operator import attrgetter
from typing import Any

from .result_entry import ResultEntry


class _NotSet:
    """
    Internal type for representing values not set.
    """


_not_set = _NotSet()


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

    def _logs_by_field_regex_match(self, field: str, reverse: bool, pattern: str) -> list[ResultEntry]:
        """
        Filter entries using regex matching.

        Parameters
        ----------
        field : str
            Name of the field to match.
        reverse : bool
            Return entries not matched.
        pattern : str | _NotSet
            Regex pattern to match.
            Underlying field value is casted to str.
        """
        if not isinstance(pattern, str):
            raise TypeError("Pattern must be a string")

        entries = []
        regex = re.compile(pattern)
        for log in self._logs:
            found_value = getattr(log, field, _not_set)
            # Field must be set.
            if isinstance(found_value, _NotSet):
                if reverse:
                    entries.append(log)
                continue

            # Value casted to "str" must be matched.
            found = regex.search(str(found_value)) is not None
            if found ^ reverse:
                entries.append(log)
        return entries

    def _logs_by_field_exact_match(self, field: str, reverse: bool, value: Any) -> list[ResultEntry]:
        """
        Filter entries by value.

        Parameters
        ----------
        field : str
            Name of the field to match.
        reverse : bool
            Return entries not matched.
        value : Any
            Exact value to match.
        """
        entries = []
        for log in self._logs:
            found_value = getattr(log, field, _not_set)
            # Field must be set.
            if isinstance(found_value, _NotSet):
                if reverse:
                    entries.append(log)
                continue

            # Type and value must be matched.
            found = isinstance(found_value, type(value)) and found_value == value
            if found ^ reverse:
                entries.append(log)
        return entries

    def _logs_by_field(
        self, field: str, reverse: bool, *, pattern: str | _NotSet = _not_set, value: Any | _NotSet = _not_set
    ) -> list[ResultEntry]:
        """
        Filter entries by type specific filtering method.

        Parameters
        ----------
        field : str
            Name of the field to match.
        reverse : bool
            Return entries not matched.
        pattern : str | _NotSet
            Regex pattern to match.
            Underlying field value is casted to str.
            Mutually exclusive with "value".
        value : Any | _NotSet
            Exact value to match.
            Mutually exclusive with "pattern".
        """
        pattern_set = not isinstance(pattern, _NotSet)
        value_set = not isinstance(value, _NotSet)

        if pattern_set and not value_set:
            return self._logs_by_field_regex_match(field, reverse, pattern)
        elif not pattern_set and value_set:
            return self._logs_by_field_exact_match(field, reverse, value)
        elif pattern_set and value_set:
            raise RuntimeError("Pattern and value parameters are mutually exclusive")
        else:
            raise RuntimeError("Either pattern or value parameters must be set")

    def contains_log(self, field: str, *, pattern: str | _NotSet = _not_set, value: Any | _NotSet = _not_set) -> bool:
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
        return len(self._logs_by_field(field, reverse=False, pattern=pattern, value=value)) > 0

    def get_logs_by_field(
        self, field: str, *, pattern: str | _NotSet = _not_set, value: Any | _NotSet = _not_set
    ) -> "LogContainer":
        """
        Get all ResultEntry messages that match the given field and pattern.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : str | _NotSet
            Regex pattern to match.
            Underlying field value is casted to str.
            Mutually exclusive with "value".
        value : Any | _NotSet
            Exact value to match.
            Mutually exclusive with "pattern".
        """
        return LogContainer(self._logs_by_field(field, reverse=False, pattern=pattern, value=value))

    def find_log(
        self, field: str, *, pattern: str | _NotSet = _not_set, value: Any | _NotSet = _not_set
    ) -> ResultEntry | None:
        """
        Find a ResultEntry message that matches the given field and pattern.
        Returns the first match or None if no match is found.
        Raises ValueError if multiple matches are found.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : str | _NotSet
            Regex pattern to match.
            Underlying field value is casted to str.
            Mutually exclusive with "value".
        value : Any | _NotSet
            Exact value to match.
            Mutually exclusive with "pattern".
        """
        findings = self._logs_by_field(field, reverse=False, pattern=pattern, value=value)
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

    def remove_logs(self, field: str, *, pattern: str | _NotSet = _not_set, value: Any | _NotSet = _not_set):
        """
        Remove all ResultEntry messages that match the given field and pattern.

        Parameters
        ----------
        field : str
            Name of the field to match.
        pattern : str | _NotSet
            Regex pattern to match.
            Underlying field value is casted to str.
            Mutually exclusive with "value".
        value : Any | _NotSet
            Exact value to match.
            Mutually exclusive with "pattern".
        """
        self._logs = self._logs_by_field(field, reverse=True, pattern=pattern, value=value)

    def group_by(self, attribute: str) -> dict[str, "LogContainer"]:
        """
        Group ResultEntry messages by a specified attribute.
        Returns a dictionary where the keys are the unique values of the attribute,
        and the values are LogContainer instances containing the grouped logs.
        """
        sorted_logs_by_attr = sorted(self._logs, key=attrgetter(attribute))
        grouped = groupby(sorted_logs_by_attr, key=attrgetter(attribute))
        return {key: LogContainer(list(group)) for key, group in grouped}
