# DSA Practice Generators

Interactive, terminal-based quiz generators for CSE310 Midterm 2. Each script generates a **random question**, waits for you to think, then reveals the full answer with step-by-step explanations and ASCII tree diagrams. Every run produces fresh questions — no memorizing the same examples.

---

## Disclaimer

This tool is provided **for educational and personal practice purposes only**. It is intended to help students study and reinforce their understanding of data structures concepts — it is not intended to facilitate, enable, or assist academic dishonesty of any kind.

While reasonable effort has been made to ensure correctness, **no guarantee is made that the generated questions, answers, or explanations are free from errors**. The outputs of this tool should not be treated as a definitive or authoritative reference. Users are encouraged to verify any answers against their course materials, textbook, or instructor.

**By using this tool, you agree that:**
- You are solely responsible for how you use it and for verifying its outputs.
- The author is not liable for any academic penalties, incorrect understanding, or any other damages — direct or indirect — arising from the use or misuse of this tool.
- This tool is not affiliated with, endorsed by, or representative of any academic institution or course.

---

## Files

| File | Topic |
|---|---|
| `BST_practice.py` | Binary Search Trees |
| `heaps_practice.py` | Min-Heaps & Max-Heaps |
| `234_trees.py` | 2-3-4 Trees & Red-Black Tree conversion |

---

## How to Run

```bash
python BST_practice.py
python heaps_practice.py
python 234_trees.py
```

Requires Python 3.7+. No external dependencies.

---

## BST Practice (`BST_practice.py`)

### Question Types

| # | Topic | What it asks |
|---|---|---|
| 1 | Two traversals → BST layout | Given any two of inorder/preorder/postorder, reconstruct and draw the BST |
| 2 | Two traversals → All traversals | Given two traversals, find all four (inorder, preorder, postorder, level-order) |
| 3 | Is it a valid BST? | Displays a tree (sometimes corrupted); answer Yes/No, with inorder proof |
| 4 | Is it a balanced BST? | Displays a BST; answer Yes/No, with per-node height breakdown |
| 5 | Array → BST layout | Given an array, insert left-to-right and draw the result |
| 6 | Random | Picks any of the above at random |

### How It Works

- Press **ENTER** after reading the question to reveal the answer.
- The answer always includes an ASCII diagram of the tree.
- For validity/balance questions (~50% chance of each), the answer explains exactly which node caused a violation.

---

## Heap Practice (`heaps_practice.py`)

All heaps use **1-based indexing**: `arr[0] = None` (unused), root at `arr[1]`, parent of `i` is `i // 2`, children are `2i` and `2i+1`.

### Question Types

| # | Topic | What it asks |
|---|---|---|
| 1 | Array → Heap | Given a plain array, build a min- or max-heap using Floyd's algorithm (sift-down from `n//2` to `1`) |
| 2 | Is it a valid heap? | Shows a heap as an array or tree diagram; answer Yes/No, with violation details |
| 3 | Heap → Sorted array | Given a heap, repeatedly extract the root to produce a sorted list |
| 4 | Convert Min-Heap ↔ Max-Heap | Convert between heap types using Floyd's heapify; shows each swap step |
| 5 | Random | Picks any of the above at random |

### How It Works

- Q4 (convert heap) has a **two-stage reveal**: first ENTER shows the tree view of the source heap, second ENTER shows the full conversion steps and result.
- Answers for Q1 and Q4 show every individual swap: `swap idx 3 ↔ idx 1 → [None, 5, 8, 12, ...]`

---

## 2-3-4 Tree Practice (`234_trees.py`)

### Question Types

| # | Topic | What it asks |
|---|---|---|
| 1 | Is it a valid 2-3-4 tree? | Shows a tree; answer Yes/No and identify which property is violated |
| 2 | Array → 2-3-4 tree | Insert values one by one; show step-by-step splits and final tree |
| 3 | 2-3-4 Tree → Red-Black Tree | Convert a 2-3-4 tree to its equivalent Red-Black Tree structure |
| 4 | Insert value | Given a tree and a value, trace the insertion with all splits shown |
| 5 | Delete value | Given a tree and a value, trace the deletion (handles merges and rotations) |
| 6 | Search for value | Trace the search path through the tree, node by node |
| 7 | Random | Picks any of the above at random |

### 2-3-4 Tree Properties (checked in Q1)
- Every node has 1–3 keys, sorted within the node
- Every internal node with k keys has exactly k+1 children
- BST ordering holds throughout
- All leaves are at the same depth

---

## Customizing Questions

All randomness comes from Python's `random.Random()` seeded from system time, so every run is different. To **reproduce a specific question**, pass a fixed seed:

```python
# In any script's main(), change:
rng = random.Random()
# to:
rng = random.Random(42)   # replace 42 with any integer
```

### Changing Question Difficulty

- **Tree size**: Each question generator calls `rng.randint(min, max)` for `n` (the number of nodes/values). Find the relevant `def q_*` function and adjust those bounds.
- **Value range**: Values are sampled from `range(1, 100)`. Change `100` to a smaller number (e.g. `50`) for simpler arithmetic.

For example, to make BST questions always use 8–10 nodes instead of 5–12, in `BST_practice.py`:

```python
# In q_two_traversals_to_bst:
n = rng.randint(5, 12)   # original
n = rng.randint(8, 10)   # smaller range, more consistent size
```

### Adding a New Question Type

1. Write a function `def q_my_topic(rng):` that prints the question and returns a `show_answer` callable.
2. Add it to the `QUESTIONS` list near the bottom of the file.
3. Update the menu's random option upper bound if needed (it auto-sizes based on `len(QUESTIONS)`).

---

## Tips for Exam Prep

- Use **option 6/5/7** (Random) to simulate exam conditions — you won't know the topic in advance.
- For traversal questions, try to answer **before** pressing ENTER. Check your work against the ASCII tree.
- For heap/2-3-4 questions, work through the steps on paper first, then compare against the step-by-step answer.
- Run the script multiple times in a row — each session generates entirely new trees and values.
