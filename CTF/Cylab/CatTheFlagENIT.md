# Securinets ENIT CTF 2026 — writeups

 <img width="1735" height="278" alt="image" src="https://github.com/user-attachments/assets/d094cf71-d92f-4c2c-ad28-e8cf3f90f142" />

Writeups for the challenges I cleared today so far : i c ant deny i didnt use AI however for real purposes such as finding the right script or fetching a public information but using MCP as the first weapon without even knowing the usage of tools is true garbage and nonsense, i enjoyed the DFIR challenges and only 3 Rev challenges .
---
 
## 1. `chz` — Reverse Engineering
 
Got handed an ELF, not stripped, calling itself a "minimal checksum/compression helper":
 
```
$ ./chz test
chz v1.4.2 - minimal checksum/compression helper
input: test
length: 4 bytes
checksum: 0xd87f7e0c
```
 
Four functions stood out right away: `legit_crc`, `backdoor_crc`, `resolve_crc`, `magic_obf`.
 
`main` calls `resolve_crc()` through what looks like an IFUNC-style indirect call and uses whatever pointer comes back to do the checksum. `resolve_crc` pretends to pick between the two CRC implementations, but the "decision" variable is hardcoded:
 
```asm
mov DWORD PTR [rbp-4], 1
cmp DWORD PTR [rbp-4], 0
jne .backdoor
lea rax, [legit_crc]   ; dead code, never reached
.backdoor:
lea rax, [backdoor_crc]
```
 
So it's always `backdoor_crc`. `legit_crc` is just a normal bitwise CRC32. `backdoor_crc` behaves like one too — unless the input is exactly 11 bytes and matches a secret hidden in `magic_obf` (XORed with `0x5a`). Hit that and it XORs 47 bytes of `flag_enc` with the recovered 11-byte key, repeating, then dumps the result to stderr disguised as an "integrity exception 0x4c15" message.
 
```python
d = open('chz', 'rb').read()
magic = d[0x2020:0x202b]        # magic_obf, 11 bytes
flag  = d[0x2040:0x2040 + 47]   # flag_enc, 47 bytes
 
key = bytes(b ^ 0x5a for b in magic)
print(key)  # b'Ji4T4n_1337'
print(bytes(c ^ key[i % 11] for i, c in enumerate(flag)))
```
 
Confirmed by just running it with the recovered key:
 
```
$ ./chz Ji4T4n_1337
[chz] integrity exception 0x4c15 — dumping diagnostic token:
securinets{1funC_r3s0lv3r_sl1ps_1n_th3_sh4d0ws}
```
 
**Flag:** `securinets{1funC_r3s0lv3r_sl1ps_1n_th3_sh4d0ws}`
 
Moral of the story: when something calls itself a "resolver," don't trust that it actually resolves anything — check whether the branch is live or dead.
 
---
 
## 2. Light Yagami's message — Vigenère
 
 
Ciphertext:
 
```
JixcmiyvxnMiie{faimmsszt_rqgl_eieiaaec_sexs_oo_xv}
```
 
Letters shift, punctuation doesn't move — classic Vigenère. The flag format hands you a free crib: `SecurinetsENIT`, 14 letters, lined up against the first 14 ciphertext letters `JixcmiyvxnMiie`.
 
Working out `key = (cipher - plain) mod 26` at each position:
 
```
17  4 21  8 21  0 11  |  17  4 21  8 21  0 11
 R  E  V  I  V  A  L  |   R  E  V  I  V  A  L
```
 
Key's `REVIVAL`, repeating — fits the theme, Light getting his memories (and ownership) back. The index only advances on letters; try advancing it on the underscores too and you get garbage.
 
```python
c = 'JixcmiyvxnMiie{faimmsszt_rqgl_eieiaaec_sexs_oo_xv}'
k = 'REVIVAL'
out, j = '', 0
for ch in c:
    if ch.isalpha():
        base = 65 if ch.isupper() else 97
        out += chr((ord(ch) - base - (ord(k[j % 7]) - 65)) % 26 + base)
        j += 1
    else:
        out += ch
print(out)
```
 
Comes out to `SecurinetsEnit{ownership_will_transfer_back_to_me}`. First submit with the stated `ENIT` capitalization got rejected — turns out the author's actual casing is `Enit`, lowercase nit, confirmed once I hit the same thing on the next challenge.
 
**Flag:** `SecurinetsEnit{ownership_will_transfer_back_to_me}`
 
---
 
## 3. Two intercepted messages — key reuse
 
.
 
Two hex ciphertexts, A (35 bytes) and B (25 bytes). A one-time pad is only safe if the key never repeats between messages — the challenge description is basically telling you it did.
 
XOR the two ciphertexts together and the key cancels out, leaving `P_A ^ P_B`. From there it's crib dragging: assume A starts with `SecurinetsENIT{`, XOR that against A directly, and the key falls out — `casefile`, repeating every 8 bytes.
 
```python
a = bytes.fromhex('30041010140002001712360b0f1d17365013165c392f5d1c2751063a0521582850550e')
b = bytes.fromhex('2e2436313928383a2e28372b2f2e24313c3e3024352c335554')
k = b'casefile'
print(bytes(c ^ k[i % 8] for i, c in enumerate(a)))
print(bytes(c ^ k[i % 8] for i, c in enumerate(b)))
```
 
```
b'SecurinetsEnit{S3re9_F1yD0u_cH4M34}'
b'MEET_AT_MIDNIGHT__CASE_07'
```
 
B decrypting cleanly to a full sentence confirms the key over its 25 bytes. A runs 10 bytes longer than B, so those trailing bytes aren't double-checked by B, but the key keeps repeating and the closing `}` lines up right where it should, so I'm confident in it.
 
**Flag:** `SecurinetsEnit{S3re9_F1yD0u_cH4M34}`
 
---
 
## 4. Rats in a Maze v1.0 — Misc / scripting
 
```bash
openssl s_client -quiet -connect misc.securinets-enit.club:1325
```
 
"A simple captcha to prove you are not a robot. Naturally, only a robot could solve it." Fair enough. The server wants a redpwn proof of work, then throws 100 back-to-back 11x11 mazes at you, 5 seconds each, answered as a string of `U`/`D`/`L`/`R`.
 
Looked straightforward until I actually started parsing it. Five things bit me before this worked:
 
1. **ANSI everywhere.** Each cell's wrapped in color codes, strip them before reading anything.
2. **Wide glyphs break `.split()`.** Mahjong tiles, cards, dominoes are double-width and eat their separator space, so naive splitting gives rows that aren't 11 cells long. Strip all whitespace from the row and take characters one at a time instead.
3. **Entrance/exit aren't grid cells.** They're colored segments on the border itself — green (ANSI 92) for the entrance, red (91) for the exit. A segment on the top border at column `c` is the virtual cell `(-1, c)`, and so on for the other sides. Treating them as normal open cells on the edge gives paths that are just wrong (`RR` instead of `DRRR`, that kind of thing).
4. **It's cheapest path, not shortest.** The server replies with `Cost: N` and checks against it. BFS gets you through the first couple rounds by luck, then fails. Needed Dijkstra.
5. **The decorative glyphs are the actual weights.** Entering a cell costs `1 + weight(glyph)`; stepping out the exit costs 1 flat.
The server is nice enough to print `Expected path:` on a failed round, which turned into a free oracle for fitting glyph weights — reconstruct both paths cell by cell, diff which glyphs show up on only one of them, adjust, repeat. 40 recorded failures later I had a weight table that matched all 40 exactly.
 
The one bug that cost real time: about 1 round in 66 still failed with an otherwise-correct table. Diffing those paths pointed at the last four domino tiles (U+1F090–1F093) — I'd priced them 9-12 pips, server treats them as 0, probably because its own domino table stops short of those. Fixed that and the remaining failures disappeared.
 
```python
from pwn import *
import subprocess, re, heapq
 
context.log_level = 'error'
HOST, PORT, N = 'misc.securinets-enit.club', 1325, 11
ANSI = re.compile(r'\x1b\[([0-9;]*)m')
DIRS = {(-1, 0): 'U', (1, 0): 'D', (0, -1): 'L', (0, 1): 'R'}
 
 
def val(ch):
    cp = ord(ch)
    if ch == '·': return 0
    if 0x1F000 <= cp <= 0x1F006: return cp - 0x1F000 + 1
    if 0x1F007 <= cp <= 0x1F00F: return cp - 0x1F007 + 1
    if 0x1F010 <= cp <= 0x1F018: return cp - 0x1F010 + 1
    if 0x1F019 <= cp <= 0x1F021: return cp - 0x1F019 + 1
    if 0x1F022 <= cp <= 0x1F02B: return 1
    if 0x1F031 <= cp <= 0x1F061: i = cp - 0x1F031; return i // 7 + i % 7
    if 0x1F063 <= cp <= 0x1F08F: i = cp - 0x1F063; return i // 7 + i % 7
    if 0x1F090 <= cp <= 0x1F093: return 0
    if 0x1F0A1 <= cp <= 0x1F0DE: return min(cp & 0xF, 10)
    if 0x2680 <= cp <= 0x2685: return cp - 0x2680 + 1
    if 0x2654 <= cp <= 0x265F:
        return {0: 100, 1: 9, 2: 5, 3: 3, 4: 3, 5: 1}[(cp - 0x2654) % 6]
    return 0
 
 
def toks(line):
    out, color, i = [], '0', 0
    while i < len(line):
        m = ANSI.match(line, i)
        if m:
            color, i = m.group(1), m.end(); continue
        out.append((line[i], color)); i += 1
    return out
 
 
def parse(text):
    lines = text.replace('\r', '').split('\n')
    top = next(i for i, l in enumerate(lines) if '╔' in l)
    bot = next(i for i, l in enumerate(lines) if '╚' in l)
    marks, grid = {}, []
 
    def mark(color, cell):
        p = color.split(';')
        if '92' in p: marks['S'] = cell
        elif '91' in p: marks['G'] = cell
 
    tt = toks(lines[top])
    for c in range(N):
        for _, col in tt[2 + 2 * c: 4 + 2 * c]: mark(col, (-1, c))
    tt = toks(lines[bot])
    for c in range(N):
        for _, col in tt[2 + 2 * c: 4 + 2 * c]: mark(col, (N, c))
    for r, row in enumerate(lines[top + 1:bot]):
        tt = toks(row)
        mark(tt[0][1], (r, -1)); mark(tt[-1][1], (r, N))
        grid.append([ch for ch, _ in tt[1:-1] if not ch.isspace() and ch != '\ufe0f'])
    return grid, marks
 
 
def solve(grid, marks):
    s, t = marks['S'], marks['G']
    dist, prev, pq = {s: 0}, {s: None}, [(0, s)]
    while pq:
        d, cur = heapq.heappop(pq)
        if d > dist.get(cur, 1e18): continue
        if cur == t: break
        for (dr, dc), m in DIRS.items():
            n = (cur[0] + dr, cur[1] + dc)
            if n == t:
                w = 1
            elif 0 <= n[0] < N and 0 <= n[1] < N and grid[n[0]][n[1]] != '#':
                w = 1 + val(grid[n[0]][n[1]])
            else:
                continue
            if d + w < dist.get(n, 1e18):
                dist[n], prev[n] = d + w, (cur, m)
                heapq.heappush(pq, (d + w, n))
    out, cur = [], t
    while prev[cur]:
        cur, m = prev[cur]; out.append(m)
    return ''.join(reversed(out)), dist[t]
 
 
def read_round(io):
    buf = b''
    while b's):' not in buf:
        try: chunk = io.recv(timeout=10)
        except EOFError: break
        if not chunk: break
        buf += chunk
    return buf.decode(errors='replace')
 
 
def clean_board(data):
    ls = [ANSI.sub('', l) for l in data.split('\n')]
    return '\n'.join(l for l in ls if l.strip().startswith(('║', '╔', '╚')))
 
 
io = remote(HOST, PORT, ssl=True)
io.recvuntil(b'sh -s ')
chal = io.recvline().strip().decode()
sol = subprocess.check_output(f'curl -sSfL https://pwn.red/pow | sh -s {chal}', shell=True).strip()
io.sendlineafter(b'solution:', sol)
 
last = None
for i in range(100):
    data = read_round(io)
    head = ANSI.sub('', data.split('╔')[0])
    if 's):' not in data:
        print(head.strip())
        if last:
            with open('fail.txt', 'a') as f:
                f.write(head + last[2] + '\nmine: ' + last[0] + f' (cost {last[1]})\n\n')
        break
    grid, marks = parse(data)
    ans, cost = solve(grid, marks)
    last = (ans, cost, clean_board(data))
    io.sendline(ans.encode())
    print(f'round {i + 1} sent, predicted cost {cost}')
 
print(ANSI.sub('', io.recvall(timeout=5).decode(errors='replace')))
```
 
Ran it in a retry loop since the occasional round still failed before the domino fix:
 
```bash
rm -f fail.txt
for i in $(seq 1 20); do
  python3 solve.py > out.txt 2>&1
  grep -q INCORRECT out.txt || break
  echo "attempt $i failed"
done
tail -8 out.txt
```
 
After round 100 the flag prints as figlet ASCII art across several lines — a few characters are ambiguous in that font (3/E, 1/l/i, 0/o), so I rendered candidate strings with `pyfiglet` and compared line by line instead of guessing.
 
**Flag:** `SecurinetsENIT{...}` — printed as ASCII art once all 100 rounds clear.
 
---
 
## 5. WASM-MAZE — Reverse
 
Given `maze.wat`, a WebAssembly text file. The "maze" part is a decoy:
 
```wat
(module
  (memory (export "memory") 1)
  (func (export "unlock") (result i32)
    i32.const 68 i32.const 33 i32.const 18 ... i32.const 143   ;; 40 constants
    i32.const 0
    i32.const 0
    i32.store8
    i32.const 1)
  (data (i32.const 128) "WASM-MAZE"))
```
 
`unlock` just pushes 40 byte constants, stores a 0, returns 1 — no actual maze logic. Those 40 constants are the encrypted flag. The `"WASM-MAZE"` string in the data segment looks like it should be the XOR key, but XORing with it just gives noise.
 
Flag format is `SecurinetsENIT{...}`, so XOR the constants against the known prefix `Securinets` and look at the key bytes that come out: `23, 68, 113, 158, 203, 248, 37, 82, 127, 172`. Consecutive differences are all 45 mod 256 — not a fixed repeating key, an arithmetic progression instead.
 
```python
v = [68,33,18,235,185,145,75,55,11,223,156,72,122,52,246,205,211,103,44,49,
     246,173,152,77,61,5,246,191,112,111,51,229,195,187,124,95,12,241,166,143]
 
print(bytes(a ^ ((23 + 45 * i) % 256) for i, a in enumerate(v)).decode())
```
 
**Flag:** `SecurinetsENIT{w4sm_memory_is_not_magic}`
 
---
 
Common thread across today's batch: the flag format itself is almost always a free crib. Use it to recover Vigenère keys, break reused XOR/OTP keys, or spot a non-repeating keystream like the WASM one. And never trust a "resolver" or a "maze" to actually do what its name says — check what it does, not what it's called.
 
