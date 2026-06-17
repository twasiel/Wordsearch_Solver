# Word Search Solver

A Python **GUI** tool that solves word search puzzles in **all 8 directions** — because apparently someone forgot to update the README the last time they shipped a feature *and* a completely different interface. It finds words, highlights matches with a warm amber overlay via `matplotlib`, renders them inside a zoomable dark-themed window, and politely tells you which words are missing (if any).

---

## Features

- **Horizontal search** — left→right and right→left (`word[::-1]` covers both)
- **Vertical search** — top→bottom and bottom→top
- **Diagonal search (↘ and ↙)** — yes, actually implemented, despite what you may have heard
- **Visual output** — renders a highlighted `wordsearch.png` via `matplotlib` (cells get a `#ffd54f` amber glow, bold text, the works), then *immediately displays it in-app* — no need to open a file manager like it's 2003
- **Zoomable canvas** — scroll to zoom (anchored to cursor position), double-click to fit-to-window; zoom clamped to `[0.05×, 20×]` so you can't accidentally LANCZOS yourself into oblivion
- **Dark theme** — full VS Code–inspired dark palette applied to all `ttk` widgets and `matplotlib` figures; your eyes are safe
- **Word list panel** — found words rendered in `#6dbf67` (green ✓), missing ones in `#e05252` (red ✗), because traffic-light UX is universally understood
- **Performance timing** — solve time reported in milliseconds via `time.perf_counter()` in the status bar
- **Decoupled highlight mask** — a separate `highlight[j][i]` boolean matrix tracks found cells with zero coupling to the grid data itself — O(x·y) extra memory, clean separation of concerns

---

## Requirements

```bash
pip install matplotlib pillow
```

Standard library: `tkinter`, `time`, `os` (no extra install needed, obviously).

> `Pillow` is now required — the GUI uses `PIL.Image` + `ImageTk.PhotoImage` for in-app rendering and `Image.LANCZOS` resampling during zoom. `matplotlib` still handles the actual grid rendering; PIL just bridges it to the canvas.

---

## Usage

```bash
python main.py
```

No args, no flags. A window opens. You pick a file. You press **Solve**. Revolutionary. 🖱️

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
| `row_i` | Each row of the word search grid, as a plain string of characters |

> Input is lowercased internally, so `CAT`, `cat`, and `CaT` are all equivalent. The solver is case-insensitive; your keyboard can relax.

### Example

**`input.txt`:**
```
5 4
cat dog
catxd
oxxxo
gxxxg
xxxxx
```

After pressing **Solve**:

- The canvas renders `wordsearch.png` with amber-highlighted cells
- The word list shows `✓ cat`, `✓ dog` (or `✗ dog` if it's hiding somewhere unreasonable)
- The status bar reports something like:

```
Solved in 0.214 ms  ·  2 found  ·  0 not found  ·  PNG → /path/to/wordsearch.png
```

**Output file:** `wordsearch.png` — saved alongside the input file, also displayed directly in the app canvas.

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
- Bold, uppercased letter text in `#1a1a1a`

Non-highlighted cells get a dark `#2a2a2a` background with a `#3d3d3d` border — fitting right into the overall dark theme. The figure scales with grid size via `CELL_SIZE = 0.6` inches/cell, saved at 150 DPI to `wordsearch.png` (next to the input file).

The saved PNG is then loaded via `PIL.Image.open()`, resampled with `Image.LANCZOS` at the current zoom level, and rendered onto a `tk.Canvas` with scrollbars. Zoom is anchored to the cursor using scroll-position math:

```
xview_moveto(cx / old_w - event.x / new_w)
```

...which keeps the canvas-world point under the cursor pinned as image dimensions change. It's just a fixed-point constraint — nothing scary. 📐

---

## GUI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  [Input file: ___________________] [Browse…] | [Solve]      │  ← top bar
├──────────────┬──────────────────────────────────────────────┤
│  Words       │  Puzzle (zoomable canvas)                    │
│  ✓ cat  (green)│                                            │
│  ✗ dog  (red) │   [rendered wordsearch.png here]            │
│              │                                              │
├──────────────┴──────────────────────────────────────────────┤
│  Solved in 0.2 ms · 1 found · 1 not found · PNG → ...      │  ← status bar
└─────────────────────────────────────────────────────────────┘
```

The left/right panels are a `ttk.PanedWindow` — drag the sash to redistribute space. The canvas supports horizontal and vertical scrollbars for grids larger than the viewport.

---

## Limitations

- **No input validation** — malformed input will raise a runtime error and display it in a `messagebox.showerror`. You've been warned.
- **Overlapping words** share highlight cells harmlessly (cosmetically fine, logically correct).
- **Single-file only** — no batch processing. One puzzle at a time, like a civilized human being.
- **PNG saved relative to input file** — `wordsearch.png` lands in the same directory as your input. Plan accordingly.
