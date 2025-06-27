"""Slash utility functions."""

import random
import string

_seed = random.randint(0, 2**32 - 1)


def random_id() -> str:
    global _seed
    _seed += 1
    return "_" + _int32_to_str(_feistel32(_seed))


def _feistel32(x: int) -> int:
    x = (x ^ (x >> 16)) * 0xBF58476D1CE4E5B9
    x &= 0xFFFFFFFF
    x = (x ^ (x >> 16)) * 0x94D049BB133111EB
    x &= 0xFFFFFFFF
    x = x ^ (x >> 16)
    return x & 0xFFFFFFFF


def _int32_to_str(n: int) -> str:
    chars = string.digits + string.ascii_letters
    base = len(chars)
    result = []
    for _ in range(6):
        n, r = divmod(n, base)
        result.append(chars[r])
    return "".join(reversed(result))
