from ipaddress import IPv4Address, IPv6Address
from socket import AF_INET, AF_INET6

import pytest

from testing_utils.net.address import Address


def test_address_from_raw_ipv4():
    raw_address = ("127.0.0.1", 8080)
    address = Address.from_raw(*raw_address)
    assert address.ip == IPv4Address("127.0.0.1")
    assert address.port == 8080


def test_address_from_raw_ipv6():
    raw_address = ("::1", 8080)
    address = Address.from_raw(*raw_address)
    assert address.ip == IPv6Address("::1")
    assert address.port == 8080


def test_address_from_dict_ipv4():
    address_dict = {"ip": "192.168.1.1", "port": 80}
    address = Address.from_dict(address_dict)
    assert address.ip == IPv4Address("192.168.1.1")
    assert address.port == 80


def test_address_from_dict_ipv6():
    address_dict = {"ip": "fe80::1", "port": 443}
    address = Address.from_dict(address_dict)
    assert address.ip == IPv6Address("fe80::1")
    assert address.port == 443


def test_address_to_raw():
    address = Address(IPv4Address("10.0.0.1"), 1234)
    raw = address.to_raw()
    assert raw == ("10.0.0.1", 1234)


def test_address_family_ipv4():
    address = Address(IPv4Address("192.168.0.1"), 8080)
    assert address.family() == AF_INET


def test_address_family_ipv6():
    address = Address(IPv6Address("::1"), 8080)
    assert address.family() == AF_INET6


def test_address_str_ipv4():
    address = Address(IPv4Address("127.0.0.1"), 80)
    assert str(address) == "127.0.0.1:80"


def test_address_str_ipv6():
    address = Address(IPv6Address("::1"), 443)
    assert str(address) == "[::1]:443"


def test_address_invalid_family():
    class FakeIPAddress:
        pass

    with pytest.raises(RuntimeError, match="Unsupported address family"):
        Address(FakeIPAddress(), 8080).family()


def test_address_invalid_str():
    class FakeIPAddress:
        pass

    with pytest.raises(RuntimeError, match="Unsupported address family"):
        str(Address(FakeIPAddress(), 8080))
