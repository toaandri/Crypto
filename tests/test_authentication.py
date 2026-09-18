import hashlib
import hmac

import pytest

from crypto.authentication import hmac_sha256, verify_hmac


def test_rfc4231_case_1():
    assert hmac_sha256(b"\x0b" * 20, b"Hi There").hex() == (
        "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7")


@pytest.mark.parametrize("key", [b"", b"k", b"k" * 64, b"k" * 65, b"k" * 131])
@pytest.mark.parametrize("message", [b"", b"abc", bytes(range(256))])
def test_matches_standard_library(key, message):
    assert hmac_sha256(key, message) == hmac.new(key, message, hashlib.sha256).digest()


def test_alterations_and_short_tags_rejected():
    tag = hmac_sha256(b"key", b"message")
    assert verify_hmac(b"key", b"message", tag)
    assert not verify_hmac(b"key", b"changed", tag)
    assert not verify_hmac(b"wrong", b"message", tag)
    assert not verify_hmac(b"key", b"message", tag[:-1])
    assert not verify_hmac(b"key", b"message", None)
    with pytest.raises(TypeError):
        hmac_sha256("key", b"message")
