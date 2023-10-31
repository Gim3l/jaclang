from _typeshed import SupportsLenAndGetItem
from hmac import compare_digest as compare_digest
from random import SystemRandom as SystemRandom
from typing import TypeVar

__all__ = [
    "choice",
    "randbelow",
    "randbits",
    "SystemRandom",
    "token_bytes",
    "token_hex",
    "token_urlsafe",
    "compare_digest",
]

_T = TypeVar("_T")

def randbelow(exclusive_upper_bound: int) -> int: ...
def randbits(k: int) -> int: ...
def choice(seq: SupportsLenAndGetItem[_T]) -> _T: ...
def token_bytes(nbytes: int | None = None) -> bytes: ...
def token_hex(nbytes: int | None = None) -> str: ...
def token_urlsafe(nbytes: int | None = None) -> str: ...