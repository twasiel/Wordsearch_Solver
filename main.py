import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageTk

# ── Dark palette ────────────────────────────────────────────────────────────
BG       = "#1e1e1e"   # window / canvas background
BG_PANEL = "#252526"   # panel / frame background
BG_INPUT = "#3c3c3c"   # entry / listbox background
FG       = "#d4d4d4"   # primary text
FG_DIM   = "#858585"   # secondary text
SEP      = "#444444"   # separator / border
ACCENT   = "#4fc3f7"   # highlight (unused visually but handy)
COL_OK   = "#6dbf67"   # found word
COL_MISS = "#e05252"   # missing word

# ── Matplotlib figure colors (dark) ────────────────────────────────────────
FIG_BG       = "#1e1e1e"
CELL_DARK    = "#2a2a2a"
CELL_EDGE    = "#3d3d3d"
HL_FACE      = "#ffd54f"
HL_EDGE      = "#f57f17"
TEXT_NORMAL  = "#d4d4d4"
TEXT_HL      = "#1a1a1a"
TITLE_COLOR  = "#d4d4d4"


def solve(filepath):
    """Run the solver; save wordsearch.png; return (found, remaining, elapsed, png_path)."""
    with open(filepath) as f:
        lines = [line.rstrip("\n") for line in f.readlines()]

    x, y = map(int, lines[0].split())
    words = list(lines[1].lower().split())
    wordSearch = [list(lines[2 + row].lower()) for row in range(y)]

    for idx, row_data in enumerate(wordSearch):
        if len(row_data) != x:
            raise ValueError(
                f"Row {idx} has length {len(row_data)}, expected {x}: {''.join(row_data)}"
            )

    found = []
    highlight = [[False] * x for _ in range(y)]

    start = time.perf_counter()

    for word in words:
        length = len(word)

        # Horizontal (left→right + reverse)
        for col in range(y):
            for row in range(x - length + 1):
                segment = "".join(wordSearch[col][row:row + length])
                if segment == word or segment == word[::-1]:
                    if word not in found:
                        found.append(word)
                    for k in range(length):
                        highlight[col][row + k] = True

        # Vertical (top→bottom + reverse)
        for row in range(x):
            for col in range(y - length + 1):
                segment = "".join(wordSearch[col + k][row] for k in range(length))
                if segment == word or segment == word[::-1]:
                    if word not in found:
                        found.append(word)
                    for k in range(length):
                        highlight[col + k][row] = True

        # Diagonal top-left→bottom-right (+ reverse)
        for col in range(y - length + 1):
            for row in range(x - length + 1):
                segment = "".join(wordSearch[col + k][row + k] for k in range(length))
                if segment == word or segment == word[::-1]:
                    if word not in found:
                        found.append(word)
                    for k in range(length):
                        highlight[col + k][row + k] = True

        # Diagonal top-right→bottom-left (+ reverse)
        for col in range(y - length + 1):
            for row in range(length - 1, x):
                segment = "".join(wordSearch[col + k][row - k] for k in range(length))
                if segment == word or segment == word[::-1]:
                    if word not in found:
                        found.append(word)
                    for k in range(length):
                        highlight[col + k][row - k] = True

    elapsed = time.perf_counter() - start
    remaining = [w for w in words if w not in found]

    # === MATPLOTLIB RENDERING (dark-styled, logic unchanged from main.py) ===
    CELL_SIZE = 0.6
    fig, ax = plt.subplots(figsize=(x * CELL_SIZE, y * CELL_SIZE))
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(FIG_BG)

    for col in range(y):
        for row in range(x):
            if highlight[col][row]:
                ax.add_patch(patches.Rectangle(
                    (row, col), 1, 1,
                    facecolor=HL_FACE, edgecolor=HL_EDGE, linewidth=1.5,
                ))
            else:
                ax.add_patch(patches.Rectangle(
                    (row, col), 1, 1,
                    facecolor=CELL_DARK, edgecolor=CELL_EDGE, linewidth=0.5,
                ))
            ax.text(
                row + 0.5, col + 0.5, wordSearch[col][row].upper(),
                ha="center", va="center", fontsize=14,
                fontweight="bold" if highlight[col][row] else "normal",
                color=TEXT_HL if highlight[col][row] else TEXT_NORMAL,
            )

    ax.set_xlim(0, x)
    ax.set_ylim(0, y)
    ax.invert_yaxis()
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        f"Found: {', '.join(found) if found else '(none)'}",
        fontsize=12, pad=10, color=TITLE_COLOR,
    )
    fig.tight_layout()

    out_path = os.path.join(os.path.dirname(os.path.abspath(filepath)), "wordsearch.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIG_BG)
    plt.close(fig)

    return found, remaining, elapsed, out_path


def _apply_dark_style(root):
    """Configure ttk widgets to use the dark palette."""
    st = ttk.Style(root)
    st.theme_use("clam")
    st.configure(".",
        background=BG, foreground=FG,
        fieldbackground=BG_INPUT, bordercolor=SEP,
        darkcolor=BG_PANEL, lightcolor=BG_PANEL,
        troughcolor=BG_PANEL, insertcolor=FG,
        selectbackground="#094771", selectforeground="#ffffff",
    )
    st.configure("TFrame",      background=BG)
    st.configure("TLabel",      background=BG,       foreground=FG)
    st.configure("TLabelframe", background=BG_PANEL, foreground=FG, bordercolor=SEP)
    st.configure("TLabelframe.Label", background=BG_PANEL, foreground=FG)
    st.configure("TPanedwindow", background=BG)
    st.configure("Sash", sashthickness=5, background=SEP)
    st.configure("TEntry",
        fieldbackground=BG_INPUT, foreground=FG,
        insertcolor=FG, bordercolor=SEP,
    )
    st.configure("TButton",
        background=BG_PANEL, foreground=FG,
        bordercolor=SEP, focuscolor=BG_PANEL,
    )
    st.map("TButton",
        background=[("active", "#3a3a3a"), ("pressed", "#444444")],
        foreground=[("active", "#ffffff")],
    )
    st.configure("TScrollbar",
        background="#3c3c3c", troughcolor=BG_PANEL,
        arrowcolor=FG, bordercolor=SEP,
    )
    st.configure("TSeparator", background=SEP)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Word Search Solver")
        self.geometry("1200x750")
        self.configure(bg=BG)

        self._pil_orig = None   # original PIL image from last solve
        self._tk_img   = None   # PhotoImage kept alive
        self._zoom     = 1.0
        self._cv       = None   # the puzzle tk.Canvas

        _apply_dark_style(self)
        self._build()

    # ── Layout ──────────────────────────────────────────────────────────────

    def _build(self):
        # Top bar
        bar = ttk.Frame(self, padding=(10, 7))
        bar.pack(fill="x")

        ttk.Label(bar, text="Input file:", foreground=FG_DIM).pack(side="left")
        self._path = tk.StringVar(
            value=os.path.join(os.path.dirname(os.path.abspath(__file__)), "input.txt")
        )
        ttk.Entry(bar, textvariable=self._path, width=60).pack(side="left", padx=5)
        ttk.Button(bar, text="Browse…", command=self._browse).pack(side="left")
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=12)
        ttk.Button(bar, text="Solve", command=self._solve).pack(side="left")
        ttk.Label(bar, text="scroll to zoom · double-click to fit",
                  foreground=FG_DIM, font=("", 9)).pack(side="right", padx=6)

        # Status bar
        self._status = tk.StringVar(value="Select an input file and press Solve.")
        tk.Label(self, textvariable=self._status,
                 bg=BG_PANEL, fg=FG_DIM, anchor="w",
                 padx=8, pady=3, font=("", 9)).pack(fill="x", side="bottom")
        tk.Frame(self, bg=SEP, height=1).pack(fill="x", side="bottom")

        # Main pane
        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=6, pady=(4, 0))

        # Left: word list
        wf = ttk.LabelFrame(pane, text="Words", padding=4)
        pane.add(wf, weight=1)

        self._listbox = tk.Listbox(
            wf, width=22, font=("Monospace", 11),
            bg=BG_INPUT, fg=FG, selectbackground="#094771",
            selectforeground="#ffffff", activestyle="none",
            relief="flat", borderwidth=0, highlightthickness=0,
        )
        vsb = ttk.Scrollbar(wf, command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._listbox.pack(fill="both", expand=True)

        # Right: zoomable puzzle canvas
        self._puzzle_lf = ttk.LabelFrame(pane, text="Puzzle", padding=0)
        pane.add(self._puzzle_lf, weight=6)
        self._build_canvas(self._puzzle_lf)

    def _build_canvas(self, parent):
        """Create the scrollable/zoomable canvas inside parent."""
        hbar = ttk.Scrollbar(parent, orient="horizontal")
        vbar = ttk.Scrollbar(parent, orient="vertical")
        self._cv = tk.Canvas(
            parent, bg=BG, highlightthickness=0,
            xscrollcommand=hbar.set, yscrollcommand=vbar.set,
        )
        hbar.config(command=self._cv.xview)
        vbar.config(command=self._cv.yview)

        hbar.pack(side="bottom", fill="x")
        vbar.pack(side="right",  fill="y")
        self._cv.pack(fill="both", expand=True)

        # Zoom bindings
        self._cv.bind("<Button-4>",    self._on_scroll)   # Linux scroll up
        self._cv.bind("<Button-5>",    self._on_scroll)   # Linux scroll down
        self._cv.bind("<MouseWheel>",  self._on_scroll)   # Windows / macOS
        self._cv.bind("<Double-1>",    lambda e: self._fit_zoom())

    # ── File / solve ─────────────────────────────────────────────────────────

    def _browse(self):
        p = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=os.path.dirname(self._path.get()),
        )
        if p:
            self._path.set(p)

    def _solve(self):
        path = self._path.get()
        if not os.path.isfile(path):
            messagebox.showerror("File not found", f"Cannot open:\n{path}")
            return

        self._status.set("Solving…")
        self.update_idletasks()

        try:
            found, remaining, elapsed, out_path = solve(path)
        except Exception as exc:
            messagebox.showerror("Solver error", str(exc))
            self._status.set("Error during solve.")
            return

        # Load PNG and fit to window
        self._pil_orig = Image.open(out_path)
        self.after(50, self._fit_zoom)   # defer until canvas has its real size

        # Word list
        self._listbox.delete(0, "end")
        for w in found:
            self._listbox.insert("end", f"  ✓  {w}")
            self._listbox.itemconfig("end", fg=COL_OK)
        for w in remaining:
            self._listbox.insert("end", f"  ✗  {w}")
            self._listbox.itemconfig("end", fg=COL_MISS)

        self._status.set(
            f"Solved in {elapsed * 1000:.1f} ms  ·  "
            f"{len(found)} found  ·  {len(remaining)} not found  ·  "
            f"PNG → {out_path}"
        )

    # ── Zoom / render ────────────────────────────────────────────────────────

    def _redraw(self):
        if self._pil_orig is None:
            return
        w = max(1, int(self._pil_orig.width  * self._zoom))
        h = max(1, int(self._pil_orig.height * self._zoom))
        resized = self._pil_orig.resize((w, h), Image.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(resized)
        self._cv.delete("all")
        self._cv.create_image(0, 0, anchor="nw", image=self._tk_img)
        self._cv.configure(scrollregion=(0, 0, w, h))

    def _fit_zoom(self):
        """Scale image so it fills the canvas panel."""
        if self._pil_orig is None:
            return
        self.update_idletasks()
        cw = self._cv.winfo_width()
        ch = self._cv.winfo_height()
        if cw <= 1 or ch <= 1:
            return
        iw, ih = self._pil_orig.size
        self._zoom = min(cw / iw, ch / ih) * 0.97
        self._redraw()

    def _on_scroll(self, event):
        """Zoom in/out centred on the cursor."""
        if self._pil_orig is None:
            return

        # Canvas-world coordinates of the cursor before zoom
        cx = self._cv.canvasx(event.x)
        cy = self._cv.canvasy(event.y)
        old_zoom = self._zoom

        factor = 1.12
        if event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            factor = 1 / 1.12
        self._zoom = max(0.05, min(self._zoom * factor, 20.0))

        self._redraw()

        # Adjust scroll so the image point under the cursor stays put
        old_w = max(1, int(self._pil_orig.width  * old_zoom))
        old_h = max(1, int(self._pil_orig.height * old_zoom))
        new_w = max(1, int(self._pil_orig.width  * self._zoom))
        new_h = max(1, int(self._pil_orig.height * self._zoom))

        self._cv.xview_moveto(max(0.0, cx / old_w - event.x / new_w))
        self._cv.yview_moveto(max(0.0, cy / old_h - event.y / new_h))


if __name__ == "__main__":
    App().mainloop()
