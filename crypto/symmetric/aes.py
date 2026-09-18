"""AES-128/192/256 from FIPS 197, written for study, not side-channel safety."""


def _multiply(a: int, b: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        a = ((a << 1) ^ (0x11B if a & 0x80 else 0)) & 255
        b >>= 1
    return result


def _substitution(value: int) -> int:
    # Multiplicative inverse x**254 in GF(2**8), followed by the affine map.
    inverse, base, exponent = 1, value, 254
    while exponent:
        if exponent & 1:
            inverse = _multiply(inverse, base)
        base = _multiply(base, base)
        exponent >>= 1
    result = inverse
    for shift in (1, 2, 3, 4):
        result ^= ((inverse << shift) | (inverse >> (8 - shift))) & 255
    return result ^ 0x63


SBOX = tuple(_substitution(i) for i in range(256))
INV_SBOX = tuple(SBOX.index(i) for i in range(256))


def _shift_rows(state: list[int], inverse: bool = False) -> list[int]:
    sign = -1 if inverse else 1
    return [state[4 * ((column + sign * row) % 4) + row]
            for column in range(4) for row in range(4)]


def _mix_columns(state: list[int], inverse: bool = False) -> list[int]:
    coefficients = (14, 11, 13, 9) if inverse else (2, 3, 1, 1)
    output = []
    for offset in range(0, 16, 4):
        column = state[offset:offset + 4]
        for row in range(4):
            value = 0
            for index in range(4):
                value ^= _multiply(column[index], coefficients[(index - row) % 4])
            output.append(value)
    return output


class AES:
    """16-byte block cipher with 16-, 24- or 32-byte keys.

    Table lookups and Python arithmetic are not constant-time.
    """

    block_size = 16

    def __init__(self, key: bytes):
        if not isinstance(key, bytes) or len(key) not in (16, 24, 32):
            raise ValueError("AES key must contain 16, 24 or 32 bytes")
        words = [list(key[i:i + 4]) for i in range(0, len(key), 4)]
        nk = len(words)
        self.rounds = nk + 6
        rcon = 1
        for index in range(nk, 4 * (self.rounds + 1)):
            temp = words[-1].copy()
            if index % nk == 0:
                temp = [SBOX[value] for value in temp[1:] + temp[:1]]
                temp[0] ^= rcon
                rcon = _multiply(rcon, 2)
            elif nk > 6 and index % nk == 4:
                temp = [SBOX[value] for value in temp]
            words.append([a ^ b for a, b in zip(words[index - nk], temp)])
        self._keys = [sum(words[i:i + 4], []) for i in range(0, len(words), 4)]

    def _add_key(self, state: list[int], index: int) -> list[int]:
        return [a ^ b for a, b in zip(state, self._keys[index])]

    @staticmethod
    def _validate(block: bytes) -> None:
        if not isinstance(block, bytes) or len(block) != 16:
            raise ValueError("AES block must contain exactly 16 bytes")

    def encrypt_block(self, block: bytes) -> bytes:
        self._validate(block)
        state = self._add_key(list(block), 0)
        for round_number in range(1, self.rounds + 1):
            state = _shift_rows([SBOX[value] for value in state])
            if round_number != self.rounds:
                state = _mix_columns(state)
            state = self._add_key(state, round_number)
        return bytes(state)

    def decrypt_block(self, block: bytes) -> bytes:
        self._validate(block)
        state = self._add_key(list(block), self.rounds)
        for round_number in range(self.rounds - 1, -1, -1):
            state = [INV_SBOX[value] for value in _shift_rows(state, inverse=True)]
            state = self._add_key(state, round_number)
            if round_number:
                state = _mix_columns(state, inverse=True)
        return bytes(state)
