# Crypto Lab

The local workbench runs the repository's Python algorithms behind a small
standard-library HTTP server. The interface, project README and animated code
walkthrough are in English, including form help, status updates and errors.

## Start

```console
python -m crypto.lab
```

Open `http://127.0.0.1:8000`. Use `--open` to open your default browser,
`--port 8001` to select another port, or `--port 0` to select an available one.
After installation, `crypto-lab` is an equivalent command. Stop with Ctrl+C.

| Workspace | What you can change | What you can observe |
|---|---|---|
| Fingerprints | UTF-8 message, input bit, comparison text | SHA-256 digests, changed output bits, weak hash |
| Arithmetic | Integers, modulus, exponent, factorization input | Euclid's divisions, Bézout identity, inverse, primality |
| RSA | Text and 256/512/1024-bit toy keys | Prime factors, exponents, ciphertext blocks, recovered text |
| Diffie–Hellman | Small prime, base, private exponents | Public values and independently computed shared secrets |
| AES-GCM | Message, key size or hex key, AAD | Fresh nonce, ciphertext, authentication tag, recovered message |
| Authentication | Original and changed messages, HMAC key | HMAC and educational RSA signature acceptance/rejection |
| Alice/Bob channel | Message and pre-shared key | Tampering rejection, valid delivery, replay rejection |
| Experiments | Block comparison, local attacks, live benchmark | ECB/CBC repetitions, five toy attacks, timing and allocation data |

To test GCM integrity, encrypt a message, switch to verification, change a hex
digit of the tag, and run again. The envelope is copied into the form after
encryption. A failed tag never returns decrypted content. Empty messages and
Unicode text are supported where the underlying operation accepts them.

Each run is independent. Changing inputs marks the previous result as stale;
exports are disabled until a new calculation succeeds. Switching workspaces
keeps form drafts in browser memory, without persisting them across reloads.
JSON exports include the experiment, its parameters and its computed result,
including demonstration keys when present.

## Scope and architecture

- `crypto/lab/service.py`: bounded, stateless experiment adapters.
- `crypto/lab/server.py`: loopback HTTP server and explicit static asset routes.
- `crypto/lab/static/`: HTML, CSS, JavaScript and a vector icon; no build step.
- `tests/test_lab.py`: independent algorithm references and HTTP boundary checks.
- `scripts/check_lab_ui.py`: real-browser interaction and responsive checks.

The server binds only to `127.0.0.1`. It checks Host, Origin and a custom request
header, limits JSON requests to 16 KiB, sets a restrictive Content Security
Policy and never writes experiment input to logs or disk. It processes requests
sequentially, including allocation benchmarks. It is a single-user local
learning tool; internet hosting and multi-user operation are outside its scope.
The underlying cryptography remains educational and unaudited.

Limits: hash input 512 UTF-8 bytes; general text 2048 bytes; HMAC/channel keys
256 bytes; factorization input at most 10⁹; DH prime at most 65521; RSA key
generation limited to three toy sizes. These are responsiveness limits, not
recommended cryptographic parameters.

## Design direction and references

Research reviewed on October 12, 2026:

- [GetLayers](https://www.getlayers.ai/) and [Layers](https://layers.to/explore)
  for visual composition and interface inspiration. Their templates and assets
  are not copied or bundled into the project.
- [Nielsen's usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
  for clear status, recovery and focused information.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) for contrast, keyboard operation,
  reflow, focus and meaningful alternatives to visual information.
- [W3C target-size guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
  for touch controls.
- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines)
  for semantic navigation, form labels, input states and browser behavior.

The design uses a scientific workbench, with left-aligned inputs and results,
a persistent experiment rail, and a quieter observation sheet alongside.

```text
Experiment rail | Topic and explanatory heading
                | Inputs and computed output | Observation sheet
                | Local scope and learning context
```

Color tokens: paper `#eef3fa`, ink `#202f4c`, indigo `#36399b`, lavender
`#e9e5fa`, changed bits `#af2e68`, white `#ffffff`. Georgia carries the short
explanatory headings; Bahnschrift/Aptos/Trebuchet carry controls and prose;
Cascadia Code/Consolas carry cryptographic values. System fonts keep the
interface fully offline. The 256-bit difference grid is the central visual
device, rather than a decorative backdrop. Layout changes at mobile widths;
there is no autoplay animation in the app. Visible focus, labels, live status
and textual result summaries support keyboard and assistive-technology use.

These are researched design decisions and tested behaviors, not a claim of
formal WCAG certification or universal compliance with every design rule.
