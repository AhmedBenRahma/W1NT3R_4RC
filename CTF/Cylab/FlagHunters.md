# Flag Hunters

| | |
|---|---|
| **Category** | Reverse Engineering (REV) / source code review |
| **Type of bug** | Injection into a custom interpreter (data and control share one channel) |
| **Files given** | `lyric-reader.py` |
| **Access** | Remote instance via `nc <host> <port>` |
| 

## 1. Overview

The challenge gives us the Python source of a "lyric reader". It prints a song line by line, supports a refrain that is replayed after every verse, and asks the audience to "sing along" through an `input()` prompt.

The flag is stored in `flag.txt` and placed in the **secret intro**, the first lines of the song:

```python
secret_intro = '''Pico warriors rising, puzzles laid bare,
...
The ether’s ours to conquer, ''' + flag + '\n'
```

But the reader starts at `[VERSE1]`, so the intro is never printed. Goal: **make the reader go back to line 0.**

## 2. Understanding the interpreter

The song is not just text. It is a tiny program, and `reader()` is its interpreter:

| Token | Effect |
|---|---|
| `REFRAIN` | Saves a return address, then jumps to the refrain |
| `CROWD ...` | Reads user input and **stores it in the song** |
| `RETURN` / `RETURN <n>` | Jumps to line `n` (`lip = n`) |
| `END` | Stops |
| anything else | Printed |

Each line is split on `;`, and every piece is executed as a separate command:

```python
for line in song_lines[lip].split(';'):
```

Normal flow: the first `REFRAIN;` rewrites the placeholder `RETURN` line into `RETURN <next line>`, jumps to the refrain, and the refrain ends with `RETURN <next line>`, which goes back to the verse.

## 3. The vulnerability

```python
elif re.match(r"CROWD.*", line):
    crowd = input('Crowd: ')
    song_lines[lip] = 'Crowd: ' + crowd      # <-- user input written into the program
    lip += 1
...
elif re.match(r"RETURN [0-9]+", line):
    lip = int(line.split()[1])               # <-- jump to any line
```

1. The user input replaces the `CROWD` line in `song_lines` **without any filtering**.
2. The refrain is executed again after every verse, so that modified line is **executed again**, and this time it is parsed as code.
3. `;` is the command separator, and `RETURN <n>` jumps anywhere.

So if the input contains `;RETURN 0`, the stored line becomes:

```
Crowd: ;RETURN 0
```

On the next pass, `split(';')` gives `['Crowd: ', 'RETURN 0']`. The first piece is printed, the second matches `RETURN [0-9]+` and sets `lip = 0`, which is the beginning of the song, where the flag is.

Note: the prompt appears **only once**. After that, the stored `Crowd: ...` line is simply replayed.

## 4. Exploit

Connect to the instance and answer the single `Crowd:` prompt with:

```
;RETURN 0
```

```bash
nc <host> <port>
...
Crowd: ;RETURN 0
```

On the next refrain the reader jumps to line 0 and prints the intro, including the flag at the end of the line `The ether’s ours to conquer, ...`.

`MAX_LINES = 100` is not a problem: the flag is within the first few printed lines.

### Testing locally

```bash
echo "picoCTF{test_flag}" > flag.txt
python3 lyric-reader.py
# Crowd: ;RETURN 0
```

## 5. Result

```
FLag: academy{7063........}
```
