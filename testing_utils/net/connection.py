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
