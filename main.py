import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches

x, y = map(int, input().split())
words = list(input().lower().split())
wordSearch = [list(input().lower()) for _ in range(y)]
found = []

# Boolean mask: highlight[j][i] == True iff cell (i, j) is part of a found word.
# Decoupled from the grid itself — O(x·y) extra memory, zero coupling. 👌
highlight = [[False] * x for _ in range(y)]

start = time.perf_counter()

for word in words:
    length = len(word)

    for j in range(y):  # Horizontal (left -> right)
        for i in range(x - length + 1):
            row = "".join(wordSearch[j][i:i+length])
            if row == word or row == word[::-1]:
                if word not in found:
                    found.append(word)
                for k in range(length):
                    highlight[j][i+k] = True

    for i in range(x):  # Vertical (top -> bottom)
        for j in range(y - length + 1):
            col = "".join(wordSearch[j+k][i] for k in range(length))
            if col == word or col == word[::-1]:
                if word not in found:
                    found.append(word)
                for k in range(length):
                    highlight[j+k][i] = True

    for j in range(y - length + 1):  # Diagonal left-to-right
        for i in range(x - length + 1):
            dia = "".join(wordSearch[j+k][i+k] for k in range(length))
            if dia == word or dia == word[::-1]:
                if word not in found:
                    found.append(word)
                for k in range(length):
                    highlight[j+k][i+k] = True

    for j in range(y - length + 1):  # Diagonal right-to-left
        for i in range(length - 1, x):
            dia = "".join(wordSearch[j + k][i - k] for k in range(length))
            if dia == word or dia == word[::-1]:
                if word not in found:
                    found.append(word)
                for k in range(length):
                    highlight[j + k][i - k] = True

elapsed = time.perf_counter() - start

remaining = [w for w in words if w not in found]
suffix = "these are all" if not remaining else f"rest are not there ({' '.join(remaining)})"
print(f"Found words: {' '.join(found)}, {suffix}")
print(f"Solved in {elapsed*1000:.3f}ms")

# === MATPLOTLIB RENDERING ===
# Each cell is a 1×1 unit square in data coordinates. Origin at top-left
# (we flip the y-axis), so cell (i, j) lives at the rectangle [i, i+1] × [j, j+1].
# Highlighted cells get a colored background; letters are drawn on top.

CELL_SIZE = 0.6  # inches per cell — scales the figure with grid dimensions
fig, ax = plt.subplots(figsize=(x * CELL_SIZE, y * CELL_SIZE))

for j in range(y):
    for i in range(x):
        if highlight[j][i]:
            ax.add_patch(patches.Rectangle(
                (i, j), 1, 1,
                facecolor="#ffd54f",  # warm amber for the "aha, found it" feel
                edgecolor="#f57f17",
                linewidth=1.5,
            ))
        else:
            ax.add_patch(patches.Rectangle(
                (i, j), 1, 1,
                facecolor="white",
                edgecolor="#cccccc",
                linewidth=0.5,
            ))
        ax.text(
            i + 0.5, j + 0.5, wordSearch[j][i].upper(),
            ha="center", va="center",
            fontsize=14,
            fontweight="bold" if highlight[j][i] else "normal",
            color="#1a1a1a",
        )

ax.set_xlim(0, x)
ax.set_ylim(0, y)
ax.invert_yaxis()  # row 0 at the top, matching the input
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

title = f"Found: {', '.join(found) if found else '(none)'}"
ax.set_title(title, fontsize=12, pad=10)

plt.tight_layout()
plt.savefig("wordsearch.png", dpi=150, bbox_inches="tight")
plt.show()
