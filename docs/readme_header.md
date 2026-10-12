<div align="center">

# Crypto From Scratch

**Build the algorithms. See the bits change. Understand the limits.**

Python 3.10+ · Standard-library runtime · Interactive local lab · MIT

[Start the lab](#quick-start) · [Explore the algorithms](#what-is-inside) · [Animated tour](#animated-tour) · [API](#api-reference) · [Validation](#validation) · [Documentation](docs/README.md)

</div>

An educational cryptography project that starts with Euclid and ends with an
authenticated conversation between Alice and Bob. RSA, Diffie–Hellman, SHA-256,
HMAC, Feistel, **AES-128/192/256 and AES-GCM** are implemented in readable Python.
The browser workbench calls these implementations directly, so every displayed
result comes from an actual calculation.

![Crypto Lab: a local workbench with editable inputs, a SHA-256 bit-difference grid and observation notes](docs/assets/lab.png)

> [!WARNING]
> This is a learning project, not a production cryptography library. Textbook
> RSA has no OAEP or PSS, the simulated channel uses a toy Feistel cipher and
> a tiny DH group, and the Python implementations are not audited or constant
> time. Do not use this code to protect real data.

## Quick start

From the repository root, with Python 3.10 or newer:

```console
python -m crypto.lab
```

Open **http://127.0.0.1:8000**. No installation, JavaScript build step, external
fonts or runtime dependencies are needed. Stop with Ctrl+C.

```console
python -m crypto.lab --open
python -m crypto.lab --port 8001
```

The interface, this README and the animated Python walkthrough are in English.
The original specification and deeper course notes remain in French.

**Try it:** flip one input bit in the hash workspace; compare Alice and Bob's
DH secrets; encrypt with GCM, switch to verification and change a tag digit;
then watch the channel reject tampering and a replay. Export the real results
as JSON, including their demonstration parameters.

<details>
<summary>Watch a tour of the actual interface</summary>

![Actual browser captures: SHA-256, Diffie–Hellman, GCM rejection, authenticated channel and block-mode comparison](docs/assets/lab.gif)

This GIF contains real browser screenshots of executed experiments. It is a
short tour, not a continuous screen recording. [Still desktop view](docs/assets/lab.png)
· [Mobile view](docs/assets/lab-mobile.png) · [Lab guide and design references](docs/lab.md)

</details>

## Installation

A virtual environment is recommended for development:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[test,docs]"
python -m pytest
```

On macOS/Linux, activate with `source .venv/bin/activate` instead.
For the library and lab only, use `python -m pip install -e .`.
After installation, `crypto-lab` is also available as a launcher.

| Extra | Dependencies | Purpose |
|---|---|---|
| None | Python standard library | Algorithms, examples, local browser lab |
| `test` | pytest, cryptography | Tests and independent AES/GCM references |
| `docs` | Pillow, Matplotlib | Animated examples and scientific figures |
| `ui-test` | Playwright, Pillow | Browser checks and real interface captures |

## What is inside

| Area | Implemented here | Observe in the lab |
|---|---|---|
| Number theory | Euclid, Bézout, inverses, fast modular powers, primality, prime generation, factorization | Division trace, identity and factors |
| RSA | Integer and byte/block encryption, key generation, JSON keys | Key components, ciphertext and text round trip |
| Diffie–Hellman | Validated prime-field exchange | Public values and shared secrets |
| Hashing | Weak educational hash, incremental SHA-256, avalanche measurements | A 256-bit difference grid |
| Symmetric encryption | Feistel, AES-128/192/256, PKCS#7, ECB/CBC/CTR, AES-GCM | GCM envelope and visible block repetitions |
| Authentication | HMAC-SHA256 and educational hash-then-RSA signatures | Accept/reject comparison for changed messages |
| Protocol | PSK-authenticated DH, directional keys, encrypt-then-HMAC, ordered delivery | Tampering and replay rejection |
| Experiments | Five local toy attacks, timing/allocation benchmarks, studies A–F | Executed attack results and live measurements |

The [completion matrix](docs/completion.md) maps the original V1–V14 requirements
to implementations, tests and recorded results. RSA-PSS, ECDSA and EdDSA are
explained conceptually as requested; they are not implemented APIs. The channel
is an in-memory simulation, not a network protocol or TLS implementation.

## Use the library

```python
from crypto.hashes import sha256
from crypto.symmetric import gcm_encrypt, gcm_decrypt

assert sha256(b"abc").hex() == (
    "ba7816bf8f01cfea414140de5dae2223"
    "b00361a396177a9cb410ff61f20015ad"
)

# Fixed public demonstration key. Use only for this learning example.
key = bytes(range(16))
nonce, ciphertext, tag = gcm_encrypt(b"Hello, Bob!", key, aad=b"Alice")
assert gcm_decrypt(ciphertext, key, nonce, tag, aad=b"Alice") == b"Hello, Bob!"
# A fresh random nonce was generated. Never reuse a nonce with the same key.
```

Prefer a terminal walkthrough:

```console
python -m examples.aes_gcm
python -m examples.secure_channel
python -m examples.tour
python -m experiments.attacks.run
```

## Animated tour

Open a chapter to see the animation, the executable code and its recorded
output. Each scene runs independently; steps within a scene share variables.
Animations last about 15–22 seconds and loop. A still alternative accompanies
each one. Outputs are captured from executed Python, never invented; random
keys and benchmark timings can change when regenerated.

| Foundations | Algorithms | Systems |
|---|---|---|
| [Mathematics](#demo-math) | [RSA](#demo-rsa) | [Authentication](#demo-authentication) |
| [Shared secrets](#demo-dh) | [AES](#demo-aes) | [Alice/Bob channel](#demo-channel) |
| [Hash avalanche](#demo-hash) | [Block modes and GCM](#demo-modes) | [Toy attacks](#demo-attacks) |
| | | [Benchmarks](#demo-benchmarks) |
