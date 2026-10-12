"""Verify the workbench against independent references and the HTTP boundary."""

import hashlib
import http.client
import json
import threading

import pytest

from crypto.lab.server import MAX_BODY, make_server
from crypto.lab.service import run_experiment


def experiment(action, **data):
    return run_experiment({"action": action, "data": data})["result"]


def test_hash_bit_flip_matches_hashlib():
    result = experiment("hash", message="é", bit="8")
    original = "é".encode()
    changed = bytes([original[0], original[1] ^ 128])
    assert result["digest"] == hashlib.sha256(original).hexdigest()
    assert result["changed_digest"] == hashlib.sha256(changed).hexdigest()
    assert result["difference"] == sum((a ^ b).bit_count() for a, b in zip(
        hashlib.sha256(original).digest(), hashlib.sha256(changed).digest()))


def test_hash_empty_text_comparison_and_bit_bounds():
    result = experiment("hash", message="", mode="text", comparison="")
    assert result["difference"] == 0
    assert result["digest"] == hashlib.sha256(b"").hexdigest()
    with pytest.raises(ValueError):
        experiment("hash", message="", mode="bit")
    with pytest.raises(ValueError):
        experiment("hash", message="é", bit=16)


def test_math_trace_bezout_inverse_and_factors():
    r = experiment("math", a="-240", b="46", modulus="7")
    assert r["a"] * r["x"] + r["b"] * r["y"] == r["gcd"] == 2
    assert (r["a"] * r["inverse"]) % 7 == 1
    assert r["power"] == pow(-240, 13, 7)
    assert r["factors"] == [53, 61]
    assert all(row["a"] == row["b"] * row["quotient"] + row["remainder"] for row in r["trace"])
    assert experiment("math", a=6, modulus=9)["inverse"] is None
    assert experiment("math", n=1)["factors"] == []


@pytest.mark.parametrize("message", ["", "\x00é🔐" * 20])
def test_rsa_multiblock_unicode_roundtrip(message):
    r = experiment("rsa", message=message)
    assert r["recovered"] == message
    assert int(r["p"]) * int(r["q"]) == int(r["n"])
    assert r["e"] * int(r["d"]) % int(r["phi"]) == 1
    assert r["length"] == len(message.encode())


def test_dh_reference_and_invalid_group():
    r = experiment("dh")
    assert r["alice_public"] == pow(5, 6, 23)
    assert r["bob_public"] == pow(5, 15, 23)
    assert r["alice_secret"] == r["bob_secret"] == 2
    with pytest.raises(ValueError):
        experiment("dh", prime=24)


@pytest.mark.parametrize("message", ["", "Bonjour 🔐"])
@pytest.mark.parametrize("bits", [128, 192, 256])
def test_aes_reference_and_edited_envelope(message, bits):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    r = experiment("aes", message=message, key_bits=bits, aad="contexte")
    expected = AESGCM(bytes.fromhex(r["key"])).encrypt(bytes.fromhex(r["nonce"]), message.encode(), b"contexte")
    assert expected.hex() == r["ciphertext"] + r["tag"]
    envelope = {key: r[key] for key in ("key", "nonce", "ciphertext", "tag", "aad")}
    assert experiment("aes", operation="decrypt", **envelope)["recovered"] == message
    for name in ("key", "nonce", "tag"):
        edited = dict(envelope)
        raw = bytearray.fromhex(edited[name])
        raw[0] ^= 1
        edited[name] = raw.hex()
        refused = experiment("aes", operation="decrypt", **edited)
        assert refused["verified"] is False
        assert "recovered" not in refused
    assert not experiment("aes", operation="decrypt", **{**envelope, "aad": "modifié"})["verified"]


def test_authentication_and_channel_rejections():
    r = experiment("authentication")
    assert r["hmac_valid"] and r["signature_valid"]
    assert not r["hmac_changed"] and not r["signature_changed"]
    r = experiment("authentication", message="", comparison="")
    assert r["hmac_changed"] and r["signature_changed"]
    channel = experiment("channel", message="Salut 🔐")
    assert channel["verified"] and channel["replay_rejected"] and channel["tamper_rejected"]
    assert channel["recovered"] == "Salut 🔐"


def test_modes_and_local_attack_results():
    r = experiment("experiments")
    assert len(set(r["ecb"][:-1])) == 1
    assert len(set(r["cbc"])) > 1
    a = experiment("experiments", kind="attacks")["results"]
    assert a["factorization"]["recovered_message"] == 42
    assert a["mitm"]["intercepted"]


def test_benchmarks_are_live_and_labelled():
    r = experiment("experiments", kind="benchmark")
    assert r["educational_only"] and len(r["results"]) == 11
    assert all(row["repeats"] == 3 and row["median_seconds"] >= 0 for row in r["results"])


@pytest.mark.parametrize("payload", [None, [], {"action": []}, {"action": "unknown"},
    {"action": "hash", "data": []}, {"action": "hash", "data": {"bit": True}},
    {"action": "hash", "data": {"message": "é" * 257}},
    {"action": "math", "data": {"n": 10**20}},
    {"action": "rsa", "data": {"bits": 4096}},
    {"action": "aes", "data": {"key": "oops"}},
    {"action": "channel", "data": {"key": "short"}}])
def test_work_limits_and_request_types(payload):
    with pytest.raises(ValueError):
        run_experiment(payload)


@pytest.fixture(scope="module")
def http_server():
    with make_server(0) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield server.server_address[1]
        server.shutdown()
        thread.join(timeout=3)


def request_http(port, path="/", method="GET", body=None, headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def test_http_assets_and_traversal(http_server):
    for path, mime in (("/", "text/html"), ("/app.js", "text/javascript"),
                       ("/style.css", "text/css"), ("/favicon.svg", "image/svg+xml")):
        status, headers, body = request_http(http_server, path)
        assert status == 200 and body
        assert headers["Content-Type"].startswith(mime)
        assert headers["Cache-Control"] == "no-store"
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert request_http(http_server, "/../pyproject.toml")[0] == 404
    assert request_http(http_server, headers={"Host": "evil.example"})[0] == 403


def test_http_json_and_same_origin_boundary(http_server):
    headers = {"Content-Type": "application/json", "X-Crypto-Lab": "1"}
    body = json.dumps({"action": "hash", "data": {"message": "abc", "mode": "text", "comparison": "abc"}})
    status, _, result = request_http(http_server, "/api/run", "POST", body, headers)
    assert status == 200
    assert json.loads(result)["result"]["digest"] == hashlib.sha256(b"abc").hexdigest()
    assert request_http(http_server, "/api/run", "POST", body, {"Content-Type": "application/json"})[0] == 403
    assert request_http(http_server, "/api/run", "POST", body, {**headers, "Origin":"https://evil.example"})[0] == 403
    assert request_http(http_server, "/api/run", "POST", body, {**headers, "Content-Type":"text/plain"})[0] == 415
    assert request_http(http_server, "/api/run", "POST", "{", headers)[0] == 400
    assert request_http(http_server, "/api/run", "POST", "[]", headers)[0] == 400
    assert request_http(http_server, "/api/run", "POST", "x" * (MAX_BODY + 1), headers)[0] == 413
