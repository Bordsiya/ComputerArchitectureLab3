def mask8(x: int) -> int:
    return x & 0x00FF


def mask11(x: int) -> int:
    return x & 0x07FF


def mask16(x: int) -> int:
    return x & 0xFFFF


def bit(x: int, n: int) -> int:
    return (x >> n) & 1
