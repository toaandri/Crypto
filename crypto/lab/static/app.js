"use strict";

const $ = (id) => document.getElementById(id);
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const number = (value, digits = 0) => new Intl.NumberFormat("en-US", {maximumFractionDigits: digits}).format(value);
const paths = {
  hash: '<path d="M4 5h4v4H4zm6 0h4v4h-4zm6 0h4v4h-4zM4 11h4v4H4zm6 0h4v4h-4zm6 0h4v4h-4zM4 17h4v4H4zm6 0h4v4h-4zm6 0h4v4h-4z"/>',
  math: '<path d="M5 6h14M12 2v8M5 16h14M7 13l10 7M7 20l10-7"/>',
  rsa: '<circle cx="8" cy="9" r="5"/><path d="m12 13 8 8m-5-5 3-3m0 6 3-3"/>',
  dh: '<path d="M3 7h17l-4-4m4 4-4 4M21 17H4l4-4m-4 4 4 4"/>',
  aes: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2"/>',
  authentication: '<path d="m12 2 8 4v7c0 5-8 9-8 9s-8-4-8-9V6zM8 12l3 3 5-6"/>',
  channel: '<path d="M2 5h13v10H8l-4 4v-4H2zm16 4h4v11h-4l-3 3v-5"/>',
  experiments: '<path d="M9 3h6m-5 0v7L4 20h16l-6-10V3M7 15h10"/>'
};
const icon = (key) => `<svg viewBox="0 0 24 24" aria-hidden="true">${paths[key]}</svg>`;

function field(name, label, value, options = {}) {
  const help = options.help ? `<small id="help-${name}">${options.help}</small>` : "";
  const attributes = `id="field-${name}" name="${name}" autocomplete="off" ${help ? `aria-describedby="help-${name}"` : ""}`;
  let input;
  if (options.choices) {
    input = `<select ${attributes}>${options.choices.map(([key, text]) => `<option value="${key}" ${String(value) === String(key) ? "selected" : ""}>${text}</option>`).join("")}</select>`;
  } else if (options.area) {
    input = `<textarea ${attributes} maxlength="${options.max || 2048}" ${options.hex ? 'spellcheck="false" class="mono"' : ""}>${escapeHTML(value)}</textarea>`;
  } else {
    input = `<input ${attributes} type="${options.numeric ? "number" : "text"}" ${options.numeric ? `min="${options.min ?? 0}" max="${options.max ?? 1000000}" inputmode="numeric"` : `maxlength="${options.max || 4096}"`} ${options.hex ? 'spellcheck="false" class="mono"' : ""} value="${escapeHTML(value)}">`;
  }
  return `<div class="field"><label for="field-${name}">${label}</label>${input}${help}</div>`;
}
const grid = (...children) => `<div class="field-grid">${children.join("")}</div>`;
const notes = (...paragraphs) => paragraphs.map((p) => `<p>${p}</p>`).join("");
const stations = {
  hash: {
    label: "Fingerprints", topic: "SHA-256 / Avalanche effect", title: "One bit changes everything.",
    description: "Change just one bit of the message. Compare the two fingerprints and watch the change spread through the 256 output bits.",
    button: "Calculate fingerprints", hint: "SHA-256, built from scratch", meta: "UTF-8 input",
    source: "crypto/hashes/sha256.py",
    notes: notes("<strong>A tiny change.</strong><br>Flipping one message bit can change about half the fingerprint. The exact count depends on the message.", "Each square represents an output bit. Pink squares mark the bits that changed.", "A fingerprint is not encryption: there is no key to recover the message. A hash alone does not prove who sent it."),
    fields: () => field("message", "Original message", "Hello", {area: true, max: 512, help: "Accented characters use multiple bytes. Bits are numbered from 0, most significant first."}) +
      grid(field("mode", "Modification", "bit", {choices: [["bit", "Flip one bit"], ["text", "Compare two texts"]]}), `<div id="bit-field">${field("bit", "Bit to flip", 0, {numeric: true, max: 39})}</div>`) +
      `<div id="comparison-field" hidden>${field("comparison", "Comparison text", "hello", {area: true, max: 512})}</div>`
  },
  math: {
    label: "Arithmetic", topic: "Euclid / Bézout / Prime numbers", title: "It all starts with numbers.",
    description: "Follow Euclid's divisions, find Bézout's coefficients and explore arithmetic where numbers wrap around a modulus.",
    button: "Explore the numbers", hint: "Exact integer arithmetic", meta: "Mathematical foundations", source: "crypto/math/modular.py",
    notes: notes("<strong>The remainder tells the story.</strong><br>Euclid replaces two numbers with the smaller number and the remainder of their division, until the remainder is zero.", "Bézout gives coefficients x and y such that a × x + b × y = GCD(a, b).", "The inverse of a modulo m exists exactly when their GCD is 1. Factorization here uses trial division on small numbers."),
    fields: () => grid(field("a", "Integer a", 240, {numeric: true, min: -1e12, max: 1e12}), field("b", "Integer b", 46, {numeric: true, min: -1e12, max: 1e12})) +
      grid(field("modulus", "Modulus m", 497, {numeric: true, min: 2, max: 1e12}), field("exponent", "Exponent k (aᵏ mod m)", 13, {numeric: true, max: 100000})) +
      field("n", "Number to test and factor", 3233, {numeric: true, min: 1, max: 1e9, help: "Up to 1 billion to keep trial division responsive."})
  },
  rsa: {
    label: "RSA", topic: "Public keys / Block encryption", title: "Two keys. The same message.",
    description: "Generate a key pair, encrypt text with the public key, then recover it with the private key. Every intermediate number stays visible.",
    button: "Generate keys and encrypt", hint: "A fresh key pair on every run", meta: "Educational RSA", source: "crypto/rsa/core.py",
    notes: notes("<strong>p × q = n.</strong><br>Two primes produce the modulus. The inverse of exponent e modulo φ(n) gives the private exponent d.", "Text is encoded as UTF-8 and split into blocks smaller than n. Its length is preserved to reconstruct every byte.", "Private keys are shown for learning. This raw RSA, without OAEP, reveals repetitions and is unsuitable for real data."),
    fields: () => field("message", "Text to encrypt", "Hello, RSA!", {area: true}) + field("bits", "Demonstration key size", 256, {choices: [[256,"256 bits · quick"],[512,"512 bits"],[1024,"1024 bits"]], help: "These sizes are for experiments. A larger key does not fix the missing security padding."})
  },
  dh: {
    label: "Diffie–Hellman", topic: "Key exchange / Shared secret", title: "A secret that never travels.",
    description: "Alice and Bob exchange public values. Each combines the received value with their own exponent to compute the same secret.",
    button: "Simulate the exchange", hint: "Alice and Bob, side by side", meta: "Small demonstration group", source: "crypto/diffie_hellman/exchange.py",
    notes: notes("<strong>The exponents stay private.</strong><br>Alice publishes gᵃ mod p, Bob publishes gᵇ mod p. Both compute gᵃᵇ mod p.", "The exchange alone does not verify the other person's identity. An intermediary can replace the public values.", "Small parameters keep the calculation readable. The module rejects trivial public values 0, 1 and p − 1. Some exponents produce these values; choose different exponents if that happens."),
    fields: () => grid(field("prime", "Prime number p", 23, {numeric: true, min: 5, max: 65521}), field("generator", "Base g", 5, {numeric: true, min: 2, max: 65519})) + grid(field("alice", "Alice's private exponent", 6, {numeric: true, min: 2, max: 65519}), field("bob", "Bob's private exponent", 15, {numeric: true, min: 2, max: 65519}))
  },
  aes: {
    label: "AES-GCM", topic: "Encryption / Integrity / AAD", title: "A secret, with its seal.",
    description: "Encrypt a message and authenticate its context. Then switch to verification, change the tag or ciphertext and observe a rejection.",
    button: "Encrypt and authenticate", hint: "A fresh nonce for every encryption", meta: "AES-128 / 192 / 256", source: "crypto/symmetric/gcm.py",
    notes: notes("<strong>Confidentiality and integrity.</strong><br>AES-GCM produces ciphertext and a tag. Decryption happens only after the tag is verified.", "AAD is authenticated but unencrypted context, such as a recipient's name or a header.", "A 12-byte nonce is generated for every encryption. Never reuse a nonce with the same key. The displayed key is for this demonstration."),
    fields: () => field("operation", "Operation", "encrypt", {choices: [["encrypt","Encrypt a message"],["decrypt","Verify and decrypt"]]}) +
      `<div id="aes-encrypt">${field("message", "Message", "A secret between Alice and Bob.", {area: true})}${field("key_bits", "New key size", 128, {choices:[[128,"128 bits"],[192,"192 bits"],[256,"256 bits"]]})}</div>` +
      field("key", "Hexadecimal key", "", {hex: true, help: "Leave blank when encrypting to generate a key. Otherwise use 32, 48 or 64 hexadecimal characters; this key's length determines the AES size."}) +
      field("aad", "Authenticated context (AAD)", "Alice → Bob") +
      `<div id="aes-decrypt" hidden>${field("nonce", "Hexadecimal nonce", "", {hex: true, max: 24, help:"24 hexadecimal characters (12 bytes)."})}${field("ciphertext", "Hexadecimal ciphertext", "", {area: true, hex:true, max:4096})}${field("tag", "Hexadecimal tag", "", {hex:true, max:32, help:"32 hexadecimal characters (16 bytes)."})}</div>`
  },
  authentication: {
    label: "Authentication", topic: "HMAC-SHA256 / RSA signature", title: "Has the message changed?",
    description: "Compare a proof made with a shared key and a signature made with a private key. Verify the original message, then a changed message.",
    button: "Create and verify proofs", hint: "A 512-bit RSA signature", meta: "Two proofs, two models", source: "crypto/authentication/hmac.py",
    notes: notes("<strong>Who can create the proof?</strong><br>With HMAC, anyone holding the shared key can create a valid tag. A signature requires the private key.", "The public key is enough to verify a signature. It cannot create one.", "This educational hash-then-RSA signature does not implement RSA-PSS. HMAC verifies integrity; it does not encrypt content."),
    fields: () => field("message", "Original message", "amount=10", {area:true}) + field("comparison", "Message to verify with the same proofs", "amount=90", {area:true}) + field("key", "Shared HMAC key", "shared-demo-key", {max:256})
  },
  channel: {
    label: "Alice / Bob channel", topic: "Authenticated exchange / Tampering / Replay", title: "From first contact to message.",
    description: "Establish an authenticated channel. Try delivering a tampered packet, then the original and a copy. Follow Bob's decisions in order.",
    button: "Send and test the channel", hint: "A fresh session for every run", meta: "In-memory simulation", source: "crypto/protocols/secure_channel.py",
    notes: notes("<strong>Verify before decrypting.</strong><br>The pre-shared key authenticates the DH exchange. Encryption and MAC keys are separate for each direction.", "The tag binds the session, direction, counter, IV and ciphertext. The counter detects replayed packets.", "This channel uses the educational Feistel cipher and a small DH group. It simulates a protocol; it is not a network transport or TLS."),
    fields: () => field("message", "Alice's message to Bob", "Hello Bob", {area:true}) + field("key", "Key already shared by Alice and Bob", "shared-demo-authentication-key", {max:256, help:"At least 16 UTF-8 bytes. Every run recreates both participants."})
  },
  experiments: {
    label: "Experiments", topic: "Modes / Local attacks / Measurements", title: "Put the ideas to the test.",
    description: "Observe repetitions in encrypted blocks, break deliberately tiny constructions or measure algorithm costs on your machine.",
    button: "Run the experiment", hint: "Bounded local data", meta: "Observe, then interpret", source: "experiments/",
    notes: notes("<strong>Evidence you can see.</strong><br>ECB turns identical blocks into identical ciphertext blocks. CBC chains them with an IV and hides that repetition.", "The five attacks use only fixed toy keys, passwords and numbers defined in the code. No external targets.", "Benchmarks report the median of 3 measurements. Peak Python allocations are measured separately; this is not total process memory. Speed is not proof of security."),
    fields: () => field("kind", "Experiment", "modes", {choices:[["modes","Repeated blocks · ECB versus CBC"],["attacks","Five attacks on toy constructions"],["benchmark","Measure RSA, SHA-256 and Feistel-CBC"]],help:"The ECB/CBC modes shown here use the educational Feistel cipher, with 8-byte blocks."})
  }
};

let current = "hash", revision = 0, controller, exported = null;
const drafts = new Map();
const form = $("experiment-form");
function values() { return Object.fromEntries(new FormData(form).entries()); }
function setValues(data) {
  for (const [name, value] of Object.entries(data)) {
    const input = form.elements.namedItem(name);
    if (input) input.value = value;
  }
}
function syncFields() {
  if (current === "hash") {
    const bitMode = $("field-mode").value === "bit";
    $("bit-field").hidden = !bitMode; $("comparison-field").hidden = bitMode;
    const bytes = new TextEncoder().encode($("field-message").value).length;
    $("field-bit").max = Math.max(0, bytes * 8 - 1);
    $("input-meta").textContent = `${number(bytes)} bytes / ${number(bytes * 8)} input bits`;
  }
  if (current === "aes") {
    const encrypt = $("field-operation").value === "encrypt";
    $("aes-encrypt").hidden = !encrypt; $("aes-decrypt").hidden = encrypt;
    $("run").innerHTML = `${encrypt ? "Encrypt and authenticate" : "Verify and decrypt"} <span aria-hidden="true">↗</span>`;
    $("run-hint").textContent = encrypt ? "A fresh nonce for every encryption" : "Tag verified before decryption";
  }
}
function markStale() {
  revision++; controller?.abort();
  $("run").disabled = false;
  document.querySelector(".output").setAttribute("aria-busy", "false");
  $("export").disabled = true; exported = null;
  $("result-state").className = "";
  $("result-state").textContent = "Parameters changed · run again";
  $("elapsed").textContent = "";
  $("error").hidden = true;
  form.querySelectorAll('[aria-invalid="true"]').forEach((input) => input.removeAttribute("aria-invalid"));
}
function showStation(key, restore = true) {
  if (!Object.hasOwn(stations, key)) key = "hash";
  if (restore && $("fields").children.length) drafts.set(current, values());
  revision++; controller?.abort(); current = key; exported = null;
  const station = stations[key];
  $("topic").textContent = station.topic; $("title").textContent = station.title;
  document.title = `${station.label} — Crypto Lab`;
  $("description").textContent = station.description;
  $("notes").innerHTML = station.notes; $("source").textContent = station.source;
  $("fields").innerHTML = station.fields();
  if (restore && drafts.has(key)) setValues(drafts.get(key));
  $("run").innerHTML = `${station.button} <span aria-hidden="true">↗</span>`;
  $("run").disabled = false; $("run-hint").textContent = station.hint;
  $("input-meta").textContent = station.meta;
  $("result").innerHTML = '<p class="empty-state">Your experiment results will appear here.</p>';
  $("result-state").textContent = "Ready to calculate"; $("result-state").className = "";
  $("export").disabled = true; $("elapsed").textContent = ""; $("error").hidden = true;
  document.querySelector(".output").setAttribute("aria-busy", "false");
  document.querySelectorAll(".nav-button").forEach((link) => {
    if (link.dataset.station === key) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  syncFields();
}
const pair = (label, value, mono = true) => `<div class="value-pair"><dt>${escapeHTML(label)}</dt><dd${mono ? ' class="mono"' : ""}>${escapeHTML(value)}</dd></div>`;
const list = (...pairs) => `<dl class="value-list">${pairs.join("")}</dl>`;
const badge = (valid, yes = "Valid", no = "Rejected") => `<span class="${valid ? "success" : "failure"}">${valid ? yes : no}</span>`;
const digest = (label, value, changed = false, hint = "") => `<div class="digest-row"><div class="digest-label"><span>${escapeHTML(label)}</span><span>${escapeHTML(hint)}</span></div><div class="digest-value mono${changed ? " changed" : ""}" translate="no">${escapeHTML(value)}</div></div>`;

function renderHash(r) {
  const bits = (value) => [...value].map((hex) => parseInt(hex, 16).toString(2).padStart(4, "0")).join("");
  const left = bits(r.digest), right = bits(r.changed_digest);
  const cells = [...left].map((bit, index) => `<span class="bit${bit !== right[index] ? " diff" : ""}" aria-hidden="true" title="Bit ${index} : ${bit} → ${right[index]}"></span>`).join("");
  return `<div class="bit-heading"><h3>The change, bit by bit</h3><span>${number(r.difference)} / 256 bits · ${number(r.difference / 256 * 100, 1)} %</span></div><div class="bit-grid" role="img" aria-label="${r.difference} of the 256 fingerprint bits changed; pink squares mark the differences.">${cells}</div><div class="bit-legend"><span><i class="rose"></i>Changed bit</span><span><i></i>Unchanged bit</span><span>Read left to right, then top to bottom</span></div>` +
    `<p class="observation">${r.bit === null ? "Two texts compared." : `Message bit <strong>${r.bit}</strong> was flipped.`} ${r.difference === 0 ? "These inputs have identical fingerprints." : `The change affects <strong>${number(r.difference)} output bits</strong>.`}</p>` +
    digest("Original message fingerprint", r.digest, false, "SHA-256") + digest("Fingerprint after modification", r.changed_digest, true, "SHA-256") +
    `<details class="trace"><summary>View the bytes and weak hash</summary>${list(pair("Original bytes", r.original || "(empty)"), pair("Modified bytes", r.changed || "(empty)"), pair("Weak hash / before", r.weak_digest), pair("Weak hash / after", r.weak_changed_digest))}</details>`;
}
function renderMath(r) {
  return `<div class="equation">${escapeHTML(r.a)} × (${escapeHTML(r.x)}) + ${escapeHTML(r.b)} × (${escapeHTML(r.y)}) = ${escapeHTML(r.gcd)}</div>` +
    `<div class="trace mono">${r.trace.length ? r.trace.map((row) => `${row.a} = ${row.quotient} × ${row.b} + ${row.remainder}`).join("<br>") : "No division needed: b is 0."}</div>` +
    list(pair("GCD(a, b)", r.gcd), pair(`Inverse of a mod ${r.modulus}`, r.inverse ?? "Does not exist: a and m are not coprime."), pair(`a^${r.exponent} mod m`, r.power), pair(`${r.n} is prime?`, r.prime ? "Yes" : "No", false), pair("Factorization", r.factors.length ? r.factors.join(" × ") : "1 has no prime factors."));
}
function renderRSA(r) {
  return `<p class="observation">Actual modulus: <strong>${r.bits} bits</strong>. Message: ${number(r.length)} bytes, ${number(r.blocks.length)} blocks.</p><details class="trace"><summary>Inspect the key pair's inner workings</summary>${list(pair("Prime p", r.p), pair("Prime q", r.q), pair("n = p × q", r.n), pair("φ(n)", r.phi), pair("Public exponent e", r.e), pair("Private exponent d", r.d))}</details>` +
    digest("Ciphertext blocks (integers)", r.blocks.length ? r.blocks.join("\n") : "Empty message: no blocks.") +
    `<div class="success-banner">${r.verified ? "Round trip verified." : "Round trip failed."} Recovered text: <strong>${escapeHTML(r.recovered || "(empty)")}</strong></div>`;
}
function renderDH(r) {
  const participant = (name, privateValue, publicValue) => `<div class="participant"><h3>${name}</h3><p>Private exponent: ${privateValue}</p><p>Public value</p><div class="public-value">${publicValue}</div><p>${r.generator}<sup>${privateValue}</sup> mod ${r.prime}</p></div>`;
  return `<div class="exchange">${participant("Alice", r.alice, r.alice_public)}<div class="exchange-arrow" aria-label="Exchange of public values">⇄<small>Only public values travel</small></div>${participant("Bob", r.bob, r.bob_public)}</div><div class="trace mono">Alice: ${r.bob_public}^${r.alice} mod ${r.prime} = ${r.alice_secret}<br>Bob: ${r.alice_public}^${r.bob} mod ${r.prime} = ${r.bob_secret}</div><div class="success-banner">Matching shared secret: <strong>${r.alice_secret}</strong>. The participants' identities still need authentication.</div>`;
}
function renderAES(r) {
  if (!r.verified) return `<div class="failure-banner">${escapeHTML(r.reason)} No decrypted text is returned.</div>`;
  if (!r.ciphertext && r.key === undefined) return `<div class="success-banner">Valid tag. Recovered text: <strong>${escapeHTML(r.recovered || "(empty)")}</strong></div>` + digest("Message bytes", r.recovered_hex || "(empty)");
  return digest(`${r.key_bits}-bit AES key (demonstration)`, r.key) + list(pair("Nonce (12 bytes)", r.nonce), pair("Ciphertext", r.ciphertext || "(empty)"), pair("Tag (16 bytes)", r.tag), pair("AAD", r.aad || "(empty)", false)) +
    `<div class="success-banner">Tag verified. Recovered text: <strong>${escapeHTML(r.recovered || "(empty)")}</strong></div><p class="observation">The parameters have been copied into the form. Choose “Verify and decrypt”, then change one tag digit to test integrity.</p>`;
}
function renderAuthentication(r) {
  return digest("HMAC-SHA256 of the original message", r.tag) + `<div class="table-wrap"><table><caption class="field-label">Verification using the original message's proofs</caption><thead><tr><th scope="col">Proof</th><th scope="col">Original message</th><th scope="col">Comparison text</th></tr></thead><tbody><tr><th scope="row">HMAC-SHA256</th><td>${badge(r.hmac_valid)}</td><td>${badge(r.hmac_changed)}</td></tr><tr><th scope="row">RSA signature</th><td>${badge(r.signature_valid)}</td><td>${badge(r.signature_changed)}</td></tr></tbody></table></div>` +
    `<details class="trace"><summary>View the signature and RSA public key</summary>${list(pair("Signature (integer)", r.signature), pair("Public key", r.public_key))}</details><p class="observation">If both texts are identical, both proofs stay valid. A change requires a new proof.</p>`;
}
function renderChannel(r) {
  const events = [
    ["Establish the channel", "DH transcript authenticated by the pre-shared key. Separate keys for each direction."],
    ["Deliver a tampered packet", `${r.tamper_rejected ? "Rejected: invalid tag." : "Accepted."} Bob's counter remains ready for the original.`],
    ["Deliver the original packet", `Accepted, sequence ${r.sequence}. Bob reads: ${r.recovered || "(empty)"}`],
    ["Replay the same packet", r.replay_rejected ? "Rejected: this sequence was already accepted." : "Accepted."]
  ];
  return `<ol class="timeline">${events.map(([title, detail], i) => `<li><span class="step" aria-hidden="true">${i + 1}</span><div><h3>${title}</h3><p>${escapeHTML(detail)}</p></div></li>`).join("")}</ol><details class="trace"><summary>Inspect Alice's packet</summary>${list(pair("Sequence", r.sequence), pair("IV", r.iv), pair("Ciphertext", r.ciphertext), pair("HMAC tag", r.tag))}</details>`;
}
function renderExperiments(r) {
  if (r.kind === "modes") {
    const row = (label, blocks, kind) => `<p class="block-label">${label}</p><div class="block-row">${blocks.map((block, i) => `<span class="cipher-block ${kind === "cbc" ? "unique" : (i === blocks.length - 1 && kind === "ecb" ? "last" : "")}" title="${escapeHTML(block)}">${kind === "cbc" ? block.slice(0, 4) : (kind === "ecb" && i === blocks.length - 1 ? "pad" : block.slice(0, 4))}</span>`).join("")}</div>`;
    return row("Message: eight identical 8-byte blocks", r.plaintext, "plain") + row("ECB: repetition stays visible", r.ecb, "ecb") + row("CBC: each block depends on the previous one", r.cbc, "cbc") + `<p class="observation">Hover over a block to read its 8 bytes. The final added block is PKCS#7 padding. These modes use the <strong>educational Feistel cipher</strong>, not AES.</p>`;
  }
  if (r.kind === "attacks") {
    const a = r.results;
    return list(pair("Brute force", `Key ${a.brute_force.key} recovered after ${a.brute_force.attempts} attempts out of ${a.brute_force.keyspace}.`, false), pair("Dictionary", `“${a.dictionary.password}” recovered in ${a.dictionary.attempts} attempts.`, false), pair("8-bit collision", `${a.collision.first} and ${a.collision.second} → ${a.collision.digest}, after ${a.collision.attempts} attempts.`), pair("DH interception", `Alice: ${a.mitm.alice_secret}, Bob: ${a.mitm.bob_secret}. Mallory computes both secrets.`, false), pair("RSA factorization", `${a.factorization.n} = ${a.factorization.p} × ${a.factorization.q}. Recovered message: ${a.factorization.recovered_message}.`, false)) + `<p class="observation">Results of fixed experiments, executed locally with deliberately weak parameters.</p>`;
  }
  const names = {rsa_keygen:"Generate RSA", rsa_encrypt:"Encrypt RSA", rsa_decrypt:"Decrypt RSA", sha256:"SHA-256", feistel_cbc_encrypt:"Encrypt Feistel-CBC", feistel_cbc_decrypt:"Decrypt Feistel-CBC"};
  return `<div class="table-wrap"><table><caption class="field-label">3 repetitions, requested RSA key size: 256 bits</caption><thead><tr><th scope="col">Operation</th><th scope="col">Bytes</th><th scope="col">Median (ms)</th><th scope="col">Peak Python allocations (bytes)</th></tr></thead><tbody>${r.results.map((row) => `<tr><th scope="row">${names[row.operation]}</th><td>${row.message_bytes ?? "—"}</td><td>${number(row.median_seconds * 1000, 3)}</td><td>${number(row.peak_python_bytes)}</td></tr>`).join("")}</tbody></table></div><p class="observation">Computed on your machine with Python ${escapeHTML(r.python)}. The export also includes the minimum duration and parameters of each measurement.</p>`;
}
const renderers = {hash:renderHash, math:renderMath, rsa:renderRSA, dh:renderDH, aes:renderAES, authentication:renderAuthentication, channel:renderChannel, experiments:renderExperiments};

async function run() {
  controller?.abort(); controller = new AbortController();
  const requestRevision = ++revision, action = current, data = values();
  $("error").hidden = true; $("run").disabled = true; $("export").disabled = true;
  $("result-state").className = ""; $("result-state").textContent = "Calculating…";
  document.querySelector(".output").setAttribute("aria-busy", "true");
  const start = performance.now();
  try {
    const response = await fetch("/api/run", {method:"POST", headers:{"Content-Type":"application/json", "X-Crypto-Lab":"1"}, body:JSON.stringify({action, data}), signal:controller.signal});
    const payload = await response.json();
    if (requestRevision !== revision) return;
    if (!response.ok) throw new Error(payload.error || "Calculation rejected: check your parameters.");
    const result = payload.result;
    if (action === "aes" && data.operation === "encrypt") setValues(result);
    $("result").innerHTML = renderers[action](result);
    $("result-state").textContent = "Result calculated"; $("result-state").className = "ready";
    $("elapsed").textContent = `${number(performance.now() - start, 1)} ms, including the local round trip`;
    exported = {educational_only:true, ...payload, parameters:data};
    $("export").disabled = false;
  } catch (error) {
    if (error.name === "AbortError" || requestRevision !== revision) return;
    $("error").textContent = error instanceof TypeError ? "The lab is not responding. Restart python -m crypto.lab, then try again." : error.message;
    $("error").hidden = false; $("result-state").textContent = "Needs correction";
    $("result").innerHTML = `<p class="empty-state">No result for these parameters. Correct the indicated input and run again.</p>`;
    $("elapsed").textContent = ""; exported = null;
    const namedField = error.message?.split(":", 1)[0]?.trim();
    const input = form.elements.namedItem(namedField);
    if (input && !input.closest("[hidden]")) { input.setAttribute("aria-invalid", "true"); input.focus(); }
    else { $("error").setAttribute("tabindex", "-1"); $("error").focus(); }
  } finally {
    if (requestRevision === revision) { $("run").disabled = false; document.querySelector(".output").setAttribute("aria-busy", "false"); }
  }
}

$("navigation").innerHTML = Object.entries(stations).map(([key, station]) => `<a class="nav-button" href="#${key}" data-station="${key}">${icon(key)}${station.label}</a>`).join("");
window.addEventListener("hashchange", () => { const key = location.hash.slice(1); if (Object.hasOwn(stations, key)) showStation(key); });
form.addEventListener("submit", (event) => { event.preventDefault(); run(); });
form.addEventListener("input", () => { markStale(); syncFields(); });
form.addEventListener("change", () => { markStale(); syncFields(); });
$("reset").addEventListener("click", () => { drafts.delete(current); showStation(current, false); run(); });
$("export").addEventListener("click", () => {
  if (!exported) return;
  const blob = new Blob([JSON.stringify(exported, null, 2) + "\n"], {type:"application/json"});
  const url = URL.createObjectURL(blob), link = document.createElement("a");
  link.href = url; link.download = `crypto-lab-${current}.json`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
showStation(location.hash.slice(1) || "hash", false);
run();
