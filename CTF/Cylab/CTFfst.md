# Securinets fst CTF103 — Writeups
 
Writeups for the Securinets fst CTF challenges, as part of the `w1nter arc` 100-days-of-code log.
Each section covers the method used and the flag obtained (or current status, if still in progress).
 
---
 
## Crypto
 
### 1. GTA-themed AES-128-CBC — Weak Key Derivation
 
**Status:** ✅ Solved
**Flag:** `Securinets_fst{M4ynajm0un4ch_Maynajmna_74d}`
 
#### Challenge
 
Players were given:
- `chall.py` — the (broken/incomplete) source used to generate the challenge
- `chall1.txt` — the distributed output: an AES-128-CBC ciphertext + IV
- A GTA: Vice City screenshot as a visual hint
```python
FLAG = b"Securinets_fst{################}"
KEY = b"R1R10R2<--><--><-->"
cipher = AES.new(KEY, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(FLAG, AES.block_size))
```
 
#### Vulnerability
 
`KEY` as written is 19 bytes — too long for AES-128 (16 bytes required). The literal string
`"R1R10R2<--><--><-->"` is a template: `R1R10R2` is real, and the three `<-->` placeholders
stand in for a 9-character secret suffix that must be guessed from context, giving exactly
`7 + 9 = 16` bytes.
 
The hint image (GTA: Vice City, 5-star wanted level) pointed to the game's classic cheat
codes. `R1, R1, CIRCLE, R2, ...` is the input sequence for **"Raise Wanted Level By Two Stars"**
— and `R1R10R2` is literally that code's first four inputs concatenated. Taking the full
cheat-code name as the key suffix:
 
```
KEY = b"RaiseWantedLevel"   # 16 bytes exactly
```
 
#### Exploit
 
```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
 
ct  = base64.b64decode("qs19bZF6u0uaV+ptsV7FTwgV49811m2qAr2mBhJIiODEuj35ehUUCj/pCfKpBNRX")
iv  = bytes.fromhex("2175fcdfa50db55f8b990ad890fd8e1d")
key = b"RaiseWantedLevel"
 
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
print(unpad(pt, AES.block_size))
# b'Securinets_fst{M4ynajm0un4ch_Maynajmna_74d}'
```
 
#### Takeaway
 
Key material was "obfuscated" by splicing a theme reference into a placeholder string instead
of using a real KDF. The fix is the obvious one: derive keys with a proper KDF (HKDF/PBKDF2),
never hand-assemble them from guessable fragments.
 
---
 
### 2. `lucky38` — Concurrent Blind-Schnorr Forgery (ROS attack)
 
**Status:** 🚧 In progress (exploit designed, not yet confirmed against the live server)
 
#### Challenge
 
A netcat service (`lucky38.py`) implements a DSA-style signing oracle:
 
```python
N = <1024-bit prime>
Q = <160-bit prime>,  (N-1) % Q == 0
G = <generator of order Q>
x = secret key;  public = G^x mod N
LIMIT = 192
```
 
Protocol (JSON lines over the socket):
 
| op       | request                       | response                              |
|----------|--------------------------------|----------------------------------------|
| `params` | –                              | `N, Q, G, pub, limit`                  |
| `new`    | –                              | fresh `token = G^k mod N`, session `id`|
| `stamp`  | `id`, `c` (client-chosen!)     | `z = k + c·x mod Q`                    |
| `submit` | `message`, `token`, `stamp`    | accepted if `G^z ≡ token·pub^c (mod N)`, `c = H(token, message)` |
 
Win condition: get `len(used) > issued` — i.e. successfully submit **more valid signatures
than signing (`stamp`) calls made** — and the server returns the flag.
 
#### Vulnerability
 
The `stamp` challenge `c` is entirely client-chosen and never tied to a message hash at
request time (unlike `submit`, where `c` *is* derived from `H(token, message)`). Since
`z = k + c·x mod Q` is linear, signatures are homomorphic:
 
```
z* = Σ aᵢ·zᵢ  (mod Q)        token* = Π tokenᵢ^aᵢ  (mod N)
  ⟹  G^z* = token* · pub^(Σ aᵢ·cᵢ)  (mod N)     — valid for ANY integer coefficients aᵢ
```
 
So `K` signing sessions can be combined into one *extra* forged signature, provided the
attacker can find messages `m₀, m₁, …, m_K` such that
 
```
score(token₁,m₁) + … + score(token_K,m_K) ≡ score(Πtokenᵢ, m₀)   (mod Q)
```
 
This is exactly the **ROS problem**, the well-known break of concurrent blind Schnorr
signatures (Benhamouda–Pointcheval–Zapalowicz–Vergnaud, generalized via Wagner's k-tree
birthday algorithm). With `Q` at 160 bits and `K = 128 = 2⁷` concurrent sessions
(comfortably under `LIMIT = 192`), the attack costs only `2^(160/8) = 2^20` work per list
instead of an infeasible 2¹⁶⁰ search.
 
Plan: open 128 sessions, solve the resulting ROS instance offline with Wagner's algorithm,
request the 128 "honest" stamps plus submit one extra combined forgery → `129 > 128` → flag.
 
#### Status / notes for next session
 
- Confirmed `N, Q, G` are a valid DSA-style group (`(N-1) % Q == 0`, `G^Q ≡ 1 mod N`).
- A pure bitmask-window Wagner merge was implemented first but is **mathematically broken**:
  modular wraparound (`s = (va+vb) mod Q`) corrupts previously-matched low bits at any merge
  level beyond the first, since `Q` is odd and not a multiple of `2^W`. Verified numerically.
- Switched to a magnitude/threshold-based merge (sort + binary search on exact values instead
  of bitmask windows), which avoids the wraparound corruption by construction. Implemented but
  not yet validated end-to-end — next step is finishing that validation, then running the full
  K=128 attack against the live service.
- No network egress to the CTF host from the dev sandbox used so far — remaining work needs
  to run from a machine with direct access to `challenges.securinetsfst.org:1341`.
#### Takeaway (preliminary)
 
Never let a signer issue a response to an unblinded, attacker-chosen challenge in a
concurrent-session setting — it turns the signing oracle into a linear system an attacker
can solve across many sessions at once (ROS). Real blind-signature constructions need either
a bound on concurrency, a different proof system, or explicit countermeasures to resist this.
 
---
 
## Reverse Engineering / Forensics
 
### 3. `vault` — Reverse Engineering (static)
 
**Status:** ✅ Solved
**Flag:** `Securinets_fst{w3lcome_b4cK_B0SS}`
 
**Approach:** string extraction (`strings -d vault`) revealed base64 fragments built on the
stack via consecutive 8-byte `movabs` instructions. The fragments overlapped in `strings`
output because of how the binary's 8-byte chunks were split, requiring them to be reassembled
in the order they appear in memory.
 
**Reassembled string:**
```
U2VjdXJpbmV0c19mc3R7dzNsY29tZV9iNGNLX0IwU1N9
```
 
**Decoding (base64):**
```bash
echo 'U2VjdXJpbmV0c19mc3R7dzNsY29tZV9iNGNLX0IwU1N9' | base64 -d
```
 
Verified by running the binary directly with this passcode (`Access granted.`).
 
---
 
### 4. `transactions.dat` — Forensics
 
**Status:** ✅ Solved (decoy flag confirmed)
**Flag:** `Securinets_fst{n1c3_try_go0d_b0y}`
 
**Approach:** a text+binary container file. A readable header (a "bank ledger export")
contains a base64-encoded note that turns out to be an explicit **decoy** (the decoded text
itself states there's nothing to find here). The real-looking flag is hidden in a table of
44 "binary records" mixing random noise with valid **base32** lines (recognizable by the
`A-Z2-7=` alphabet).
 
**Extracting the valid base32 lines, in order of appearance:**
```bash
strings -n 4 transactions.dat | grep -E '^[A-Z2-7=]{8}$' | tr -d '\n' | base32 -d
```
 
Flag confirmed by its own content ("nice try good boy") — the decoy *is* the flag.
 
---
 
### 5. `casino` — Pwn / Reverse Engineering (logic bug)
 
**Status:** ✅ Solved
 
**Context:** a CLI "casino" game. Buy/sell chips (Red/Blue/Black Chips), goal: reach a
balance ≥ $10,000 to redeem a "VIP Card" that prints the flag (loaded dynamically from
`flag.txt` by `load_flag`, only called once the balance condition is met).
 
**Method:** full disassembly (`objdump -d -M intel`) of every buy/sell/redeem function.
Mathematically proved that the normal buy↔sell cycle is strictly neutral (no profit
possible), by comparing the three buy functions (Red/Blue/Black) line by line.
 
**Bug found:** the **Black Chips** buy function is the only one of the three that **omits
the negative-quantity check** (`qty >= 0`) present in the Red/Blue functions. Entering a
negative quantity gives:
```
cost = price × qty = 100 × (-100) = -10000
balance -= cost  →  balance += 10000
```
Balance jumps from $100 to $10,100 in a single purchase.
 
**Exploit:**
1. Menu → `2` (Black Chips)
2. "How many?" → `-100`
3. Menu → `3` (Redeem VIP Card) → flag printed
---
 
### 6. `cipher_box` — Reverse Engineering / Crypto
 
**Status:** ✅ Solved
**Flag:** `Securinets_fst{th3_l0ck_w45_alw4ys_p4rt_0f_th3_b0x}`
 
**Context:** a command-line encryption tool (`./cipher_box <text>`). Contains a global
`DATA_BLOCK` (51 encrypted characters) presented as a "self-test reference record", never
actually processed at runtime by `main()`.
 
**Method:**
- Located functions via the binary's retained symbols (`idx_of`, `transform_a`, `transform_b`,
  `derive_legacy_key`, `main`).
- Read `main()` first: revealed that `transform_b` and `derive_legacy_key` are **never
  called** for actual encryption — they're decoys, explicitly flagged as *"deprecated,
  unrelated to this module"* in the binary's own debug messages.
- Reverse-engineered `transform_a` instruction by instruction — the real encryption
  function: a **3-round** substitution cipher using three permutation tables (`TABLE_A`,
  `TABLE_B`, `TABLE_C`, extracted with `objdump -s -j .rodata`), with a position-dependent
  offset per character:
```
A = (i + 17) mod 65
B = (i ÷ 5 + 42) mod 65
C = (i ÷ 11 + 5) mod 65
idx1 = TABLE_A[(idx + A) mod 65]
idx2 = TABLE_B[(idx1 + B) mod 65]
idx3 = TABLE_C[(idx2 + C) mod 65]
output = CHARSET[idx3]
```
- Inverted the algorithm: built inverse tables (`inv_A`, `inv_B`, `inv_C`) and applied the
  steps in reverse order on `DATA_BLOCK`.
- **Verification:** re-encrypted the resulting plaintext with the original algorithm →
  matched `DATA_BLOCK` exactly, confirming the inversion was correct.
---
 
### 7. `poker` — Reverse Engineering (in progress)
 
**Status:** 🚧 In progress
 
**Context:** a Texas Hold'em-style CLI poker game ("RAVEN'S BACK ROOM POKER v1.0"), compiled
with full debug symbols (`-g -O0`). The intro text implies the house always wins, pointing
toward exploiting a predictable RNG (`srand`/`time`) or a game-logic bug to force a win.
 
**Functions identified:**
- `get_win_key`, `frag_alpha` → `frag_omega` (6 fragments), `assemble_flag` — a fragmented
  flag mechanism, assembled/printed under some condition.
- `build_deck`, `shuffle_deck` — deck construction and shuffling (predictable-RNG lead).
- `evaluate_five`, `best_hand_from_seven`, `evaluate_winner`, `get_threshold` — hand-evaluation
  and winner-determination logic.
- `play_round`, `main` — game loop.
**Status:** analysis in progress — disassembling `get_win_key`, the `frag_*` functions, and
`assemble_flag` to determine the exact win condition and how the flag is reconstructed.
*(to be completed)*
 
---
 
## General methodology
 
**Crypto:** identify the primitive and its parameters, check for implementation weaknesses
(key length/derivation, non-standard protocol steps, unblinded challenges) before assuming the
math itself is broken; verify every candidate key/flag by actually decrypting/re-deriving it.
 
**Reverse engineering / forensics:** for each binary — string extraction (`strings`), full
disassembly (`objdump -d -M intel`), dumping data sections (`objdump -s -j .data` / `.rodata`),
manual block-by-block reading translating x86 assembly into pseudocode, then **systematic
empirical verification** of the result (running the binary, re-encrypting, or re-encoding)
before treating any flag as confirmed.
 
