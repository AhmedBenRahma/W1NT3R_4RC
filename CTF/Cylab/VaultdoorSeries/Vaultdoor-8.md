

## Solver
```python

expected = [
    0xF4, 0xC0, 0x97, 0xF0, 0x77, 0x97, 0xC0, 0xE4,
    0xF0, 0x77, 0xA4, 0xD0, 0xC5, 0x77, 0xF4, 0x86,
    0xD0, 0xA5, 0x45, 0x96, 0x27, 0xB5, 0x77, 0x95,
    0x94, 0xC1, 0xE1, 0xD2, 0xE1, 0xE1, 0xD0, 0x95,
]

swaps = [(1, 2), (0, 3), (5, 6), (4, 7), (0, 1), (3, 4), (2, 5), (6, 7)]

def switch_bits(c, p1, p2):
    if ((c >> p1) & 1) != ((c >> p2) & 1):
        c ^= (1 << p1) | (1 << p2)
    return c

def unscramble(c):
    for p1, p2 in reversed(swaps):  
        c = switch_bits(c, p1, p2)
    return c

password = "".join(chr(unscramble(b)) for b in expected)
print("academy{" + password + "}")
```

## Flag

`academy{s0m3_m0r3_b1t_sh1fTiNg_ea469661e}`
