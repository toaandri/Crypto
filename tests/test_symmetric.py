import pytest

from crypto.symmetric import (
    FeistelCipher, cbc_decrypt, cbc_encrypt, ctr_crypt, ecb_decrypt,
    ecb_encrypt, pkcs7_pad, pkcs7_unpad,
)

KEY = b"cle-pedagogique!"


def test_single_block_round_trip_and_avalanche():
    cipher = FeistelCipher(KEY)
    encrypted = cipher.encrypt_block(b"12345678")
    assert cipher.decrypt_block(encrypted) == b"12345678"
    assert encrypted != b"12345678"


@pytest.mark.parametrize("message", [b"", b"a", b"12345678", b"message avec plusieurs blocs"])
def test_ecb_round_trip(message):
    assert ecb_decrypt(ecb_encrypt(message, KEY), KEY) == message


def test_ecb_reveals_repeated_blocks():
    ciphertext = ecb_encrypt(b"REPETE!!" * 3, KEY)
    assert ciphertext[:8] == ciphertext[8:16] == ciphertext[16:24]


def test_cbc_round_trip_and_hides_repetitions():
    iv = b"12345678"
    plaintext = b"REPETE!!" * 3
    returned_iv, ciphertext = cbc_encrypt(plaintext, KEY, iv)
    assert returned_iv == iv
    assert len({ciphertext[i:i + 8] for i in range(0, 24, 8)}) == 3
    assert cbc_decrypt(ciphertext, KEY, iv) == plaintext


def test_ctr_round_trip_without_padding():
    nonce = b"abcd"
    plaintext = b"taille non alignee"
    ciphertext = ctr_crypt(plaintext, KEY, nonce)
    assert len(ciphertext) == len(plaintext)
    assert ctr_crypt(ciphertext, KEY, nonce) == plaintext


def test_padding_validation():
    assert pkcs7_unpad(pkcs7_pad(b"hello")) == b"hello"
    with pytest.raises(ValueError):
        pkcs7_unpad(b"1234567\x02")


def test_bad_key_iv_and_nonce_are_rejected():
    with pytest.raises(ValueError):
        FeistelCipher(b"short")
    with pytest.raises(ValueError):
        cbc_encrypt(b"x", KEY, b"bad")
    with pytest.raises(ValueError):
        ctr_crypt(b"x", KEY, b"bad")
