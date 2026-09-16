"""Reversible byte-block encoding around raw RSA.

The format preserves message length and leading zero bytes. It provides no
padding security and deliberately does not pretend to be OAEP.
"""

from dataclasses import dataclass

from .core import decrypt_int, encrypt_int
from .keys import PrivateKey, PublicKey


@dataclass(frozen=True)
class EncryptedMessage:
    blocks: tuple[int, ...]
    length: int

    def __post_init__(self) -> None:
        if self.length < 0 or any(block < 0 for block in self.blocks):
            raise ValueError("invalid encrypted message")


def plaintext_block_size(modulus: int) -> int:
    """Largest byte width guaranteed to encode an integer below *modulus*."""
    size = (modulus.bit_length() - 1) // 8
    if size < 1:
        raise ValueError("RSA modulus is too small for byte messages")
    return size


def encrypt_bytes(message: bytes, key: PublicKey) -> EncryptedMessage:
    block_size = plaintext_block_size(key.n)
    blocks = tuple(
        encrypt_int(int.from_bytes(message[offset:offset + block_size], "big"), key)
        for offset in range(0, len(message), block_size)
    )
    return EncryptedMessage(blocks, len(message))


def decrypt_bytes(ciphertext: EncryptedMessage, key: PrivateKey) -> bytes:
    block_size = plaintext_block_size(key.n)
    expected_blocks = (ciphertext.length + block_size - 1) // block_size
    if len(ciphertext.blocks) != expected_blocks:
        raise ValueError("ciphertext block count does not match its declared length")
    if not ciphertext.blocks:
        return b""
    output = bytearray()
    for index, block in enumerate(ciphertext.blocks):
        if block >= key.n:
            raise ValueError("ciphertext block must be smaller than n")
        width = block_size
        if index == len(ciphertext.blocks) - 1 and ciphertext.length % block_size:
            width = ciphertext.length % block_size
        decoded = decrypt_int(block, key)
        if decoded >= 1 << (8 * width):
            raise ValueError("decrypted block does not fit its expected width")
        output.extend(decoded.to_bytes(width, "big"))
    return bytes(output)


def encrypt_text(message: str, key: PublicKey, encoding: str = "utf-8") -> EncryptedMessage:
    return encrypt_bytes(message.encode(encoding), key)


def decrypt_text(ciphertext: EncryptedMessage, key: PrivateKey, encoding: str = "utf-8") -> str:
    return decrypt_bytes(ciphertext, key).decode(encoding)
