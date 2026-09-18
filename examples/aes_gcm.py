"""Run with python -m examples.aes_gcm."""

from crypto.symmetric import AES, gcm_decrypt, gcm_encrypt


def main():
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    block = bytes.fromhex("00112233445566778899aabbccddeeff")
    print("AES-128 :", AES(key).encrypt_block(block).hex())
    nonce, ciphertext, tag = gcm_encrypt(b"Bonjour Bob", key, aad=b"Alice -> Bob")
    print("GCM :", gcm_decrypt(ciphertext, key, nonce, tag, b"Alice -> Bob").decode())
    try:
        gcm_decrypt(ciphertext, key, nonce, tag, b"Mallory -> Bob")
    except ValueError:
        print("En-tete modifie : rejete")


if __name__ == "__main__":
    main()
