# Word Search Solver

A Python CLI tool that solves word search puzzles in **all 8 directions** — because apparently someone forgot to update the README the last time they shipped a feature. It finds words, highlights matches with a warm amber overlay via `matplotlib`, and politely tells you which words are missing (if any).

---

## Features

- **Horizontal search** — left→right and right→left (`word[::-1]` covers both)
- **Vertical search** — top→bottom and bottom→top
- **Diagonal search (↘ and ↙)** — yes, actually implemented, despite what you may have heard
- **Visual output** — renders a highlighted `wordsearch.png` via `matplotlib` (cells get a `#ffd54f` amber glow, bold text, the works)
- **Performance timing** — reports solve time in milliseconds via `time.perf_counter()`
- **Decoupled highlight mask** — a separate `highlight[j][i]` boolean matrix tracks found cells with zero coupling to the grid data itself — O(x·y) extra memory, clean separation of concerns
- Reports found words and identifies any that weren't located

---

## Requirements

```bash
pip install matplotlib
```

Standard library: `time` (no extra install needed, obviously).

---

## Usage

```bash
python main.py
```

The program reads from `stdin`. No args, no flags, just raw input — very "competitive programming" of it.

### Input Format

```
<X> <Y>
<word1> <word2> ... <wordN>
<row_1>
<row_2>
...
<row_Y>
```

| Parameter | Description |
|-----------|-------------|
| `X` | Grid width (number of columns) |
| `Y` | Grid height (number of rows) |
| `word1..N` | Space-separated list of words to find (case-insensitive) |
| `row_i` | Each row of the word search grid, characters separated by spaces |

> Input is lowercased internally, so `CAT`, `cat`, and `CaT` are all equivalent. The solver is case-insensitive; your keyboard can relax.

### Example

**Input:**
```
5 4
cat dog
c a t x d
o x x x o
g x x x g
x x x x x
```

**stdout:**
```
Found words: cat dog, these are all
Solved in 0.214ms
```

**Output file:** `wordsearch.png` — a rendered grid with amber-highlighted cells for all found word positions.

If not all words are found, the output changes to:
```
Found words: cat, rest are not there (dog)
```

---

## How It Works

The solver runs in **O(W · X · Y)** time, where:
- `W` = number of words to search
- `X · Y` = grid dimensions (total cells)

For each word of length `L`, it checks **4 direction families** (each also covering its reverse via `word[::-1]`):

| Direction | Iteration bounds | Slice |
|-----------|-----------------|-------|
| Horizontal | `j ∈ [0, Y)`, `i ∈ [0, X−L]` | `wordSearch[j][i : i+L]` |
| Vertical | `i ∈ [0, X)`, `j ∈ [0, Y−L]` | `wordSearch[j+k][i]` for `k ∈ [0,L)` |
| Diagonal ↘ | `j ∈ [0, Y−L]`, `i ∈ [0, X−L]` | `wordSearch[j+k][i+k]` for `k ∈ [0,L)` |
| Diagonal ↙ | `j ∈ [0, Y−L]`, `i ∈ [L−1, X)` | `wordSearch[j+k][i−k]` for `k ∈ [0,L)` |

Each candidate slice is compared against both `word` and `word[::-1]` — covering all 8 directions with 4 loops. Elegant? Arguably. Redundant iterations? Also yes.

Found cells are marked in the `highlight[j][i]` boolean mask. The grid itself is never mutated — the mask is only applied at render time by `matplotlib`.

---

## Visualization

The renderer maps each cell `(i, j)` to a `1×1` unit square in data coordinates, with the y-axis inverted so row `0` sits at the top (matching input order). Highlighted cells get:
- `facecolor="#ffd54f"` (warm amber)
- `edgecolor="#f57f17"`
- Bold, uppercased letter text

Non-highlighted cells get a plain white background with a light `#cccccc` border. The figure scales with grid size via `CELL_SIZE = 0.6` inches/cell, saved at 150 DPI to `wordsearch.png`.

---

## Limitations

- **No input validation** — malformed input will raise a runtime error. You've been warned.
- **Overlapping words** share highlight cells harmlessly (cosmetically fine, logically correct).
- **stdin only** — no file input support. Pipe it, paste it, or cry about it.
