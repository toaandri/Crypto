"""Show that equal plaintext blocks stay equal in ECB, unlike CBC."""

from crypto.symmetric import BLOCK_SIZE, cbc_encrypt, ecb_encrypt


def blocks(data: bytes) -> list[bytes]:
    return [data[i:i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]


if __name__ == "__main__":
    key = b"educational-key"
    plaintext = b"REPETE!!" * 4
    ecb = ecb_encrypt(plaintext, key)
    _, cbc = cbc_encrypt(plaintext, key, iv=b"12345678")
    print("Blocs ECB uniques:", len(set(blocks(ecb))), "/", len(blocks(ecb)))
    print("Blocs CBC uniques:", len(set(blocks(cbc))), "/", len(blocks(cbc)))
