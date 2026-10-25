#!/usr/bin/env python3
"""house-music solver: L-R -> spectrogram glyphs -> keyed pigpen -> flag.

usage: python3 solve.py files/transmission.wav
"""
import sys, wave
import numpy as np

KEY = "CRUX"                                   # "CRUX first"
ALPHA = KEY + "".join(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in KEY)

# pigpen cell for (top, left, right, bottom) edges -> index 0..8 (A..I slots)
CELLS = {(0, 0, 1, 1): 0, (0, 1, 1, 1): 1, (0, 1, 0, 1): 2,
         (1, 0, 1, 1): 3, (1, 1, 1, 1): 4, (1, 1, 0, 1): 5,
         (1, 0, 1, 0): 6, (1, 1, 1, 0): 7, (1, 1, 0, 0): 8}
WORD_GAP = 12000                               # samples of silence => word break


def load_diff(path):
    w = wave.open(path)
    a = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(int)
    return a[:, 0] - a[:, 1]                   # hidden signal = L - R


def glyph_segments(d, min_gap=2000):
    """Glyphs are separated by exact digital silence in L-R."""
    z = (d == 0).astype(int)
    edge = np.diff(np.r_[0, z, 0])
    runs = [(s, t) for s, t in zip(np.where(edge == 1)[0], np.where(edge == -1)[0])
            if t - s >= min_gap]
    # (start, end, length of the silence that follows)
    return [(runs[i][1], runs[i + 1][0], runs[i + 1][1] - runs[i + 1][0])
            for i in range(len(runs) - 1)]


def band(S, f, lo, hi):
    return S[(f >= lo) & (f <= hi)].max(axis=0)


def classify(d, s, e):
    """Read one glyph from its spectrogram. Returns the pigpen slot 0..25."""
    x = d[s:e].astype(float)
    n, hop = 512, 128
    fr = np.array([x[i:i + n] * np.hanning(n) for i in range(0, len(x) - n, hop)])
    S = np.abs(np.fft.rfft(fr, axis=1)).T
    f = np.fft.rfftfreq(n, 1 / 44100)
    top, mid, bot = band(S, f, 7000, 7700), band(S, f, 4900, 5500), band(S, f, 2700, 3300)
    thr = 0.25 * max(top.max(), bot.max())
    T = len(top)
    mid_t = slice(int(T * .25), int(T * .75))
    has_top = (top[mid_t] > thr).mean() > .8          # 7.3 kHz tone  = top edge
    has_bot = (bot[mid_t] > thr).mean() > .8          # 3.0 kHz tone  = bottom edge
    click = np.abs(x) > 4000                          # broadband click = vertical edge
    left, right = click[:1800].any(), click[-1800:].any()

    if not (has_top or has_bot or left or right):     # X-grid wedge, drawn as a sweep
        k = max(2, T // 10)
        a = {"top": top[:k].mean(), "mid": mid[:k].mean(), "bot": bot[:k].mean()}
        b = {"top": top[-k:].mean(), "mid": mid[-k:].mean(), "bot": bot[-k:].mean()}
        if a["top"] > 1.5 * a["mid"] and b["top"] > 1.5 * b["mid"]: return 18   # V  top
        if a["bot"] > 1.5 * a["mid"] and b["bot"] > 1.5 * b["mid"]: return 21   # ^  bottom
        return 20 if a["mid"] >= a["top"] else 19                               # <  / >
    cell = CELLS[(int(has_top), int(left), int(right), int(has_bot))]
    dot = (mid[int(T * .3):int(T * .7)] > 0.25 * thr).any()   # 5.2 kHz blob in the middle
    return cell + (9 if dot else 0)


def main(path):
    d = load_diff(path)
    out = ""
    for s, e, gap in glyph_segments(d):
        out += ALPHA[classify(d, s, e)]
        if gap >= WORD_GAP:
            out += "_"
    print(out)
    print(f"cruXipher{{{out.lower()}}}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "files/transmission.wav")

#Y4G4M1 Copyrights
