# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
"""
Structured representation of test log entries.
"""

__all__ = ["ResultEntry"]

import re
from typing import Any


class ResultEntry:
    """
    Structured representation of test log entries.

    Values are set as attributes, with keys changed to snake case.
    E.g., message `{"threadId": "ThreadID(1)"}` will have `threadId` key available under `entry.thread_id`.
    """

    def __init__(self, json_message: dict[str, Any]) -> None:
        """
        Create entry.

        Parameters
        ----------
        json_message : dict[str, Any]
            Message content.
        """
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

    def __getattribute__(self, name: str) -> Any:
        # NOTE: this function is passing base implementation on purpose.
        # Pylance is not able to handle autocompletion of dynamically generated attributes.
        return super().__getattribute__(name)

    def __str__(self) -> str:
        members = [f"{attr}={getattr(self, attr)}" for attr in vars(self)]
        return f"ResultEntry({', '.join(members)})"
