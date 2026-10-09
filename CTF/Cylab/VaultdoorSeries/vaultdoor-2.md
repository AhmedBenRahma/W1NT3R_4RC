after seeing the java source code
<img width="762" height="542" alt="image" src="https://github.com/user-attachments/assets/59685fca-45d2-4cc1-8668-0d0ecc9e4c8c" />



## Solver

```python
s = "jU5t_a_sna_3lpm16g84d_u_4_m7rc42"
p = [None] * 32

for i in range(8):            p[i] = s[i]
for i in range(8, 16):        p[23 - i] = s[i]
for i in range(16, 32, 2):    p[46 - i] = s[i]
for i in range(31, 16, -2):   p[i] = s[i]

print("academy{" + "".join(p) + "}")
```

## Flag

`academy{jU5t_a_s1mpl3_an4gr4m_4_u_d78c62}`
