"""ECB, CBC and CTR modes over the educational Feistel cipher."""

import secrets

from .feistel import BLOCK_SIZE, FeistelCipher


def _xor(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right, strict=True))


def pkcs7_pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    if not 1 <= block_size <= 255:
        raise ValueError("block size must be between 1 and 255")
    padding = block_size - len(data) % block_size
    return data + bytes([padding]) * padding


def pkcs7_unpad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    if not data or len(data) % block_size:
        raise ValueError("invalid padded data length")
    padding = data[-1]
    if padding == 0 or padding > block_size or data[-padding:] != bytes([padding]) * padding:
        raise ValueError("invalid PKCS#7 padding")
    return data[:-padding]


def ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Encrypt padded data in ECB mode (reveals repeated-block patterns)."""
    cipher = FeistelCipher(key)
    padded = pkcs7_pad(plaintext)
    return b"".join(cipher.encrypt_block(padded[i:i + BLOCK_SIZE]) for i in range(0, len(padded), BLOCK_SIZE))


def ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    if not ciphertext or len(ciphertext) % BLOCK_SIZE:
        raise ValueError("ECB ciphertext must be non-empty and block-aligned")
    cipher = FeistelCipher(key)
    padded = b"".join(cipher.decrypt_block(ciphertext[i:i + BLOCK_SIZE]) for i in range(0, len(ciphertext), BLOCK_SIZE))
    return pkcs7_unpad(padded)


def cbc_encrypt(plaintext: bytes, key: bytes, iv: bytes | None = None) -> tuple[bytes, bytes]:
    """Return ``(iv, ciphertext)``. A random IV is generated when omitted."""
    iv = secrets.token_bytes(BLOCK_SIZE) if iv is None else iv
    if len(iv) != BLOCK_SIZE:
        raise ValueError(f"IV must contain exactly {BLOCK_SIZE} bytes")
    cipher = FeistelCipher(key)
    previous = iv
    output = bytearray()
    padded = pkcs7_pad(plaintext)
    for offset in range(0, len(padded), BLOCK_SIZE):
        previous = cipher.encrypt_block(_xor(padded[offset:offset + BLOCK_SIZE], previous))
        output.extend(previous)
    return iv, bytes(output)


def cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    if len(iv) != BLOCK_SIZE:
        raise ValueError(f"IV must contain exactly {BLOCK_SIZE} bytes")
    if not ciphertext or len(ciphertext) % BLOCK_SIZE:
        raise ValueError("CBC ciphertext must be non-empty and block-aligned")
    cipher = FeistelCipher(key)
    previous = iv
    output = bytearray()
    for offset in range(0, len(ciphertext), BLOCK_SIZE):
        block = ciphertext[offset:offset + BLOCK_SIZE]
        output.extend(_xor(cipher.decrypt_block(block), previous))
        previous = block
    return pkcs7_unpad(bytes(output))


def ctr_crypt(data: bytes, key: bytes, nonce: bytes) -> bytes:
    """Encrypt or decrypt in CTR mode using a 4-byte nonce and counter.

    Reusing the same nonce with one key destroys confidentiality.
    """
    if len(nonce) != 4:
        raise ValueError("CTR nonce must contain exactly 4 bytes")
    blocks = (len(data) + BLOCK_SIZE - 1) // BLOCK_SIZE
    if blocks > 2**32:
        raise ValueError("data is too long for the 32-bit counter")
    cipher = FeistelCipher(key)
    output = bytearray()
    for counter, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
        stream = cipher.encrypt_block(nonce + counter.to_bytes(4, "big"))
        chunk = data[offset:offset + BLOCK_SIZE]
        output.extend(_xor(chunk, stream[:len(chunk)]))
    return bytes(output)

