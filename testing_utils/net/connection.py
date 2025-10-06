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
from socket import (
    SOCK_STREAM,
    socket,
)

from .address import Address


def create_connection(address: Address, timeout: float | None = 3.0) -> socket:
    """
    Create a socket connected to the server.

    Parameters
    ----------
    address : Address
        Address to connect to.
    timeout : float | None
        Connection timeout in seconds. 0 for non-blocking mode, None for blocking mode.
    """
    s = socket(address.family(), SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(address.to_raw())
    return s
