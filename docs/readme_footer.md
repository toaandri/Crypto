## API reference

Messages are `bytes` unless an API explicitly accepts text. Use UTF-8
`.encode()` / `.decode()` for text. Byte-to-integer encoding is big-endian.
Invalid mathematical parameters, malformed envelopes and failed authentication
raise `ValueError`; APIs requiring bytes may raise `TypeError`.

| Module | Main interfaces | Contract |
|---|---|---|
| `crypto.math` | `gcd`, `extended_gcd`, `mod_inverse`, `mod_pow` | Bézout returns `(g, x, y)`; inverse needs coprime inputs; modular powers support negative exponents when an inverse exists |
| `crypto.math` | `is_prime`, `is_probable_prime`, `generate_prime`, `factorize` | Trial division for small numbers; deterministic Miller–Rabin bases below `2**64`, random witnesses above; prime generation uses `secrets` |
| `crypto.rsa` | `generate_keypair`, `PublicKey`, `PrivateKey` | Returns `(public, private)`; JSON serialization is available; private-key JSON is unencrypted |
| `crypto.rsa` | `encrypt_int`, `decrypt_int` | Requires an integer in `[0, n)`; textbook RSA |
| `crypto.rsa` | `encrypt_bytes`, `decrypt_bytes`, `encrypt_text`, `decrypt_text` | Preserves byte length and leading zeroes using `EncryptedMessage(blocks, length)`; no security padding |
| `crypto.diffie_hellman` | `Party(prime, generator, private=None)` | `.public` and `.shared_secret(peer_public)`; no peer authentication |
| `crypto.hashes` | `sha256(data)`, `SHA256(data=b"")`, `educational_hash` | SHA-256 returns 32 bytes; incremental `.update()`, `.digest()`, `.hexdigest()`; weak hash is deliberately unsuitable for security |
| `crypto.symmetric` | `AES(key)` | 16/24/32-byte keys; `.encrypt_block()` and `.decrypt_block()` operate on one 16-byte block |
| `crypto.symmetric` | `FeistelCipher`, `ecb_encrypt/decrypt`, `cbc_encrypt/decrypt`, `ctr_crypt` | Educational 8-byte block cipher; CBC returns `(iv, ciphertext)`; CTR uses a 4-byte nonce |
| `crypto.symmetric` | `gcm_encrypt`, `gcm_decrypt` | AES-GCM, 16-byte tags, AAD support; encryption returns `(nonce, ciphertext, tag)`; verify before decrypting |
| `crypto.authentication` | `hmac_sha256`, `verify_hmac` | 32-byte tags; constant-time tag comparison via `secrets.compare_digest` |
| `crypto.signatures` | `sign(message, private)`, `verify(message, signature, public)` | Educational hash-then-RSA; modulus must accommodate all 256-bit digests; no PSS |
| `crypto.protocols` | `Handshake`, `establish_channels`, `SecureChannel`, `Packet` | PSK-authenticated handshake, one-use completion, directional keys, 64-bit counters; rejects replay, reflection and unordered delivery |

For a fixed composite and independent random Miller–Rabin witnesses, the false
acceptance bound is `4**(-rounds)`. This is not a posterior probability that an
accepted number is composite. Below `2**64`, the implementation uses a fixed
seven-base deterministic test instead.

Further explanations: [mathematics](docs/mathematics/fondations.md),
[RSA and OAEP](docs/cryptography/rsa.md), [Diffie–Hellman](docs/cryptography/diffie_hellman.md),
[SHA-256](docs/cryptography/hash.md), [symmetric modes](docs/cryptography/symmetric.md),
[AES-GCM](docs/cryptography/aes_gcm.md), [authentication](docs/cryptography/authentication.md),
[the channel](docs/cryptography/secure_channel.md). These course notes are in French.

## Experiments and reproducibility

![Recorded studies of factorization, primality, avalanche and Diffie–Hellman cost](docs/assets/science.png)

The [A–F report](docs/experiments.md) describes hypotheses, protocols, measured
results and limits. [Recorded science data](docs/results/science.json) includes
inputs, repetitions and platform information. Timings depend on Python, the
machine and random prime generation; they do not establish cryptographic security.

```console
python -m experiments.avalanche.run
python -m experiments.modes.ecb_vs_cbc
python -m experiments.benchmarks.run --key-sizes 256 512 --message-sizes 16 256 --repeats 3
python -m experiments.science.run
```

The last command refreshes the scientific results. Benchmark timing and Python
allocation peaks are measured separately. Allocation peaks are not total process
RAM. The five toy attacks are local brute force, dictionary search, truncated
hash collision, unauthenticated DH interception and tiny RSA factorization.

Regenerate the English walkthrough and figures from the executable examples:

```console
python -m scripts.build_docs
python -m scripts.verify_docs
```

The README is generated from `docs/readme_header.md`, `examples/tour.py` and
`docs/readme_footer.md`; edit those sources so regeneration preserves changes.
The original study report remains in French.

## Validation

```console
python -m pytest
python -m scripts.verify_docs
```

The suite covers independent SHA-256/HMAC references, AES/GCM known-answer
vectors and `cryptography` comparisons, number-theory properties, Unicode and
block boundaries, invalid keys/inputs, authenticated transcripts, tampering,
replay and the workbench's local HTTP boundary. Passing tests are evidence of
specified behavior, not a cryptographic audit.

To check the UI and regenerate actual browser captures:

```console
python -m pip install -e ".[ui-test]"
python -m playwright install chromium
python -m crypto.lab
```

In another terminal:

```console
python -m scripts.check_lab_ui --publish-assets
```

Browser checks exercise all eight workspaces, three experiment modes, JSON
export, GCM rejection, HTML escaping, invalid inputs, keyboard focus, deep links,
offline feedback and layouts at 320, 390, 768 and 1440 CSS pixels. Captures land
in the ignored `output/playwright/` directory; `--publish-assets` refreshes the
README's desktop/mobile images and interface GIF. Browser dependencies are
optional and never used by the crypto library or lab server.

[GitHub Actions](.github/workflows/tests.yml) runs the Python suite on 3.10,
3.12 and 3.14, checks documentation, and runs a Chromium UI check. A local pass
does not imply the hosted workflow has already run.

## Repository map

```text
crypto/          Number theory, ciphers, hashes, authentication and protocols
  lab/           Local HTTP workbench and offline browser assets
examples/        Runnable demonstrations and the animated walkthrough source
experiments/     Avalanche, block modes, attacks, benchmarks and studies A–F
tests/           Algorithm, protocol and workbench tests
scripts/         Documentation generation, verification and browser checks
docs/            Explanations, design references, figures and measured JSON
maharavo.txt     Original project specification
```

## Security scope

- Algorithms are readable educational implementations, without constant-time
  guarantees or third-party audit.
- AES-GCM validates reference vectors, but reference compatibility does not make
  this Python implementation suitable for real secrets.
- Raw RSA, tiny DH parameters, visible demonstration keys and the custom Feistel
  cipher are intentional learning devices.
- The lab listens only on loopback, stores no requests/results, loads no remote
  assets, and limits expensive inputs. It is a single-user local tool.
- Use audited cryptographic libraries and established protocols for real systems.

See the [detailed limitations](docs/security/limitations.md) and
[lab guide](docs/lab.md) for precise boundaries.

## Contributing and license

Follow [CONTRIBUTING.md](CONTRIBUTING.md), run the relevant checks, and keep
algorithm explanations and executable demonstrations consistent. The project
uses the [MIT license](LICENSE). Changes are recorded in [CHANGELOG.md](CHANGELOG.md).
