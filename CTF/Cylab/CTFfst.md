# Securinets FST CTF — Writeups
 
Writeups for a series of reverse engineering / forensics challenges (Securinets FST). Each section covers the method used and the flag obtained.
 
---
 
## 1. `vault` — Reverse Engineering (static)
 
**Approach:** string extraction (`strings -d vault`) revealed base64 fragments built on the stack via consecutive 8-byte `movabs` instructions. The fragments overlapped in `strings` output because of how the binary's 8-byte chunks were split, requiring them to be reassembled in the order they appear in memory.
 
**Reassembled string:**
```
U2VjdXJpbmV0c19mc3R7dzNsY29tZV9iNGNLX0IwU1N9
```
 
**Decoding (base64):**
```bash
echo 'U2VjdXJpbmV0c19mc3R7dzNsY29tZV9iNGNLX0IwU1N9' | base64 -d
```
 
**Flag:**
```
Securinets_fst{w3lcome_b4cK_B0SS}
```
 
Verified by running the binary directly with this passcode (`Access granted.`).
 
---
 
## 2. `transactions.dat` — Forensics
 
**Approach:** a text+binary container file. A readable header (a "bank ledger export") contains a base64-encoded note that turns out to be an explicit **decoy** (the decoded text itself states there's nothing to find here). The real flag is hidden in a table of 44 "binary records" mixing random noise with valid **base32** lines (recognizable by the `A-Z2-7=` alphabet).
 
**Extracting the valid base32 lines, in order of appearance:**
```bash
strings -n 4 transactions.dat | grep -E '^[A-Z2-7=]{8}$' | tr -d '\n' | base32 -d
```
 
**Flag (decoy, confirmed by its own content "nice try good boy"):**
```
Securinets_fst{n1c3_try_go0d_b0y}
```
 
---
 
## 3. `casino` — Pwn / Reverse Engineering (logic bug)
 
**Context:** a CLI "casino" game. Buy/sell chips (Red/Blue/Black Chips), goal: reach a balance ≥ $10,000 to redeem a "VIP Card" that prints the flag (loaded dynamically from `flag.txt` by the `load_flag` function, only called once the balance condition is met).
 
**Method:** full disassembly (`objdump -d -M intel`) of every buy/sell/redeem function. Mathematically proved that the normal buy↔sell cycle is strictly neutral (no profit possible), by comparing the three buy functions (Red/Blue/Black) line by line.
 
**Bug found:** the **Black Chips** buy function is the only one of the three that **omits the negative-quantity check** (`qty >= 0`) present in the Red/Blue functions. Entering a negative quantity gives:
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
 
## 4. `cipher_box` — Reverse Engineering / Crypto
 
**Context:** a command-line encryption tool (`./cipher_box <text>`). Contains a global `DATA_BLOCK` (51 encrypted characters) presented as a "self-test reference record", never actually processed at runtime by `main()`.
 
**Method:**
- Located functions via the binary's retained symbols (`idx_of`, `transform_a`, `transform_b`, `derive_legacy_key`, `main`).
- Read `main()` first: revealed that `transform_b` and `derive_legacy_key` are **never called** for actual encryption — they're decoys, explicitly flagged as *"deprecated, unrelated to this module"* in the binary's own debug messages.
- Reverse-engineered `transform_a` instruction by instruction — the real encryption function: a **3-round** substitution cipher using three permutation tables (`TABLE_A`, `TABLE_B`, `TABLE_C`, extracted with `objdump -s -j .rodata`), with a position-dependent offset per character:
```
  A = (i + 17) mod 65
  B = (i ÷ 5 + 42) mod 65
  C = (i ÷ 11 + 5) mod 65
  idx1 = TABLE_A[(idx + A) mod 65]
  idx2 = TABLE_B[(idx1 + B) mod 65]
  idx3 = TABLE_C[(idx2 + C) mod 65]
  output = CHARSET[idx3]
```
- Inverted the algorithm: built inverse tables (`inv_A`, `inv_B`, `inv_C`) and applied the steps in reverse order on `DATA_BLOCK`.
- **Verification:** re-encrypted the resulting plaintext with the original algorithm → matched `DATA_BLOCK` exactly, confirming the inversion was correct.
**Flag:**
```
Securinets_fst{th3_l0ck_w45_alw4ys_p4rt_0f_th3_b0x}
```
 
---
 
## 5. `poker` — Reverse Engineering (in progress)
 
**Context:** a Texas Hold'em-style CLI poker game ("RAVEN'S BACK ROOM POKER v1.0"), compiled with full debug symbols (`-g -O0`). The intro text implies the house always wins, pointing toward exploiting a predictable RNG (`srand`/`time`) or a game-logic bug to force a win.
 
**Functions identified:**
- `get_win_key`, `frag_alpha` → `frag_omega` (6 fragments), `assemble_flag` — a fragmented flag mechanism, assembled/printed under some condition.
- `build_deck`, `shuffle_deck` — deck construction and shuffling (predictable-RNG lead).
- `evaluate_five`, `best_hand_from_seven`, `evaluate_winner`, `get_threshold` — hand-evaluation and winner-determination logic.
- `play_round`, `main` — game loop.
**Status:** analysis in progress — disassembling `get_win_key`, the `frag_*` functions, and `assemble_flag` to determine the exact win condition and how the flag is reconstructed. *(to be completed)*
 
---
 
## General methodology
 
For each binary: string extraction (`strings`), full disassembly (`objdump -d -M intel`), dumping data sections (`objdump -s -j .data` / `.rodata`), manual block-by-block reading translating x86 assembly into pseudocode, then **systematic empirical verification** of the result (running the binary or re-encrypting/re-encoding) before treating any flag as confirmed.
 
