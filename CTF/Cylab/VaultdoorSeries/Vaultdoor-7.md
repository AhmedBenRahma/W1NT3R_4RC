
## Solver
```python

xs = [1096770097, 1952395366, 1600270708, 1601398833,
      1716808014, 1734291814, 1698116193, 926442085]

password = "".join(x.to_bytes(4, "big").decode() for x in xs)
print("academy{" + password + "}")

```

## Flag

`academy{A_b1t_0f_b1t_sh1fTiNg_1fe72a78be}`
