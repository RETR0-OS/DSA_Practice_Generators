#!/usr/bin/env python3
"""
Heap Exam Practice Tool
Covers: array→heap, heap→array, is valid heap, min↔max conversion.
All output is deterministic via the random library.

Heaps are 1-indexed: arr[0] = None (unused), root at arr[1].
  Parent of i   : i // 2
  Left child    : 2 * i
  Right child   : 2 * i + 1
"""

import random


# ─────────────────────────────────────────────
#  HEAP TREE PRETTY-PRINTER
#  Same bottom-up width algorithm as bst_practice.py
# ─────────────────────────────────────────────

class _HNode:
    """Lightweight node used only for display."""
    def __init__(self, val):
        self.val   = val
        self.left  = None
        self.right = None


def _array_to_display_tree(arr):
    """
    Build a display tree from a 1-indexed heap array (arr[0] is None/ignored).
    Nodes live at indices 1..len(arr)-1.
    Parent i -> left child 2i, right child 2i+1.
    """
    if len(arr) <= 1:
        return None
    nodes = [None] + [_HNode(arr[i]) for i in range(1, len(arr))]
    for i in range(1, len(arr)):
        li, ri = 2 * i, 2 * i + 1
        if li < len(arr):
            nodes[i].left  = nodes[li]
        if ri < len(arr):
            nodes[i].right = nodes[ri]
    return nodes[1]


def _display_aux(node):
    """
    Recursively compute display lines for a subtree.
    Returns (lines, width, height, root_offset).
    """
    label = str(node.val)
    w = len(label)

    if node.left is None and node.right is None:
        return [label], w, 1, w // 2

    if node.right is None:
        ll, lw, lh, lx = _display_aux(node.left)
        first  = ' ' * (lx + 1) + '_' * (lw - lx - 1) + label
        second = ' ' * lx + '/' + ' ' * (lw - lx - 1 + w)
        pad    = [line + ' ' * w for line in ll]
        return [first, second] + pad, lw + w, lh + 2, lw + w // 2

    if node.left is None:
        rl, rw, rh, rx = _display_aux(node.right)
        first  = label + '_' * rx + ' ' * (rw - rx)
        second = ' ' * (w + rx) + '\\' + ' ' * (rw - rx - 1)
        pad    = [' ' * w + line for line in rl]
        return [first, second] + pad, w + rw, rh + 2, w // 2

    ll, lw, lh, lx = _display_aux(node.left)
    rl, rw, rh, rx = _display_aux(node.right)

    first  = (' ' * (lx + 1)
              + '_' * (lw - lx - 1)
              + label
              + '_' * rx
              + ' ' * (rw - rx))
    second = (' ' * lx + '/'
              + ' ' * (lw - lx - 1 + w + rx)
              + '\\'
              + ' ' * (rw - rx - 1))

    if lh < rh:
        ll += [' ' * lw] * (rh - lh)
    elif rh < lh:
        rl += [' ' * rw] * (lh - rh)

    middle = [l + ' ' + r for l, r in zip(ll, rl)]
    return [first, second] + middle, lw + w + rw, len([first, second] + middle), lw + w // 2


def pretty_print_heap(arr):
    """
    Print the 1-indexed heap array as a properly aligned binary tree.
    arr[0] is None and is not printed in the tree.
    """
    if len(arr) <= 1:
        print("  (empty heap)")
        return
    root = _array_to_display_tree(arr)
    lines, _, _, _ = _display_aux(root)
    for line in lines:
        print('  ' + line)


def print_indexed_array(arr):
    """
    Print a 1-indexed heap array with index labels beneath.
    Index 0 is shown as 'None' to make the convention explicit.
    """
    entries = ['None'] + [f'{v:>3}' for v in arr[1:]]
    vals = '  [ ' + ', '.join(entries) + ' ]'
    idxs = '    ' + '   '.join(f'{i:>1}' for i in range(len(arr)))
    print(vals)
    print(idxs)


def _fmt_snap(arr):
    """Format a 1-indexed snapshot for step-trace output."""
    entries = ['None'] + [str(v) for v in arr[1:]]
    return '[' + ', '.join(entries) + ']'


# ─────────────────────────────────────────────
#  CORE HEAP OPERATIONS  (all 1-indexed)
# ─────────────────────────────────────────────

def _cmp(a, b, is_min):
    """Return True if a should be above b in this heap type."""
    return a < b if is_min else a > b


def _sift_down(arr, i, end, is_min):
    """
    Sift element at 1-based index i downward within arr[1..end].
    Returns list of swap steps: (idx_a, idx_b, snapshot).
    """
    steps = []
    while True:
        target = i
        l, r   = 2 * i, 2 * i + 1
        if l <= end and _cmp(arr[l], arr[target], is_min):
            target = l
        if r <= end and _cmp(arr[r], arr[target], is_min):
            target = r
        if target == i:
            break
        arr[i], arr[target] = arr[target], arr[i]
        steps.append((i, target, list(arr)))
        i = target
    return steps


def _sift_up(arr, i, is_min):
    """
    Sift element at 1-based index i upward.
    Returns list of swap steps: (idx_a, idx_b, snapshot).
    """
    steps = []
    while i > 1:
        parent = i // 2
        if _cmp(arr[i], arr[parent], is_min):
            arr[i], arr[parent] = arr[parent], arr[i]
            steps.append((i, parent, list(arr)))
            i = parent
        else:
            break
    return steps


def build_heap_floyd(values, is_min):
    """
    Build a 1-indexed heap from a plain list of values using Floyd's algorithm.
    arr[0] = None, real elements at arr[1..n].
    Returns (heap_arr, all_steps).
    """
    arr = [None] + list(values)    # 1-based; index 0 unused
    n   = len(arr) - 1
    all_steps = []
    for i in range(n // 2, 0, -1):
        steps = _sift_down(arr, i, n, is_min)
        all_steps.extend(steps)
    return arr, all_steps


def is_valid_heap(arr, is_min):
    """
    Check heap property on a 1-indexed array (arr[0] ignored).
    For every node i, arr[i] must satisfy the heap property against its children.
    """
    n = len(arr) - 1
    for i in range(1, n + 1):
        for child in (2 * i, 2 * i + 1):
            if child <= n:
                if not _cmp(arr[i], arr[child], is_min) and arr[i] != arr[child]:
                    return False
    return True


def heap_to_sorted_array(arr, is_min):
    """
    Repeatedly extract the root from a 1-indexed heap to produce a sorted list.
    Returns (sorted_list, steps) where each step = (extracted_val, heap_snapshot).
    """
    a   = list(arr)        # copy; a[0] = None
    end = len(a) - 1
    extracted = []
    steps     = []
    while end >= 1:
        val      = a[1]
        a[1], a[end] = a[end], a[1]
        end     -= 1
        _sift_down(a, 1, end, is_min)
        extracted.append(val)
        # snapshot only the live portion [None, ...active elements...]
        steps.append((val, [None] + a[1:end + 1]))
    return extracted, steps


def convert_heap(arr, from_min_to_max):
    """Convert between heap types by rebuilding with Floyd's algorithm."""
    values = arr[1:]       # strip the None sentinel
    return build_heap_floyd(values, is_min=not from_min_to_max)


# ─────────────────────────────────────────────
#  RANDOM DATA GENERATORS
# ─────────────────────────────────────────────

def random_heap_type(rng):
    return rng.choice([True, False])    # True = min-heap


def heap_label(is_min):
    return "Min-Heap" if is_min else "Max-Heap"


def random_valid_heap(rng, n, is_min):
    """Generate a valid 1-indexed heap array of n real elements."""
    vals    = rng.sample(range(1, 100), n)
    heap, _ = build_heap_floyd(vals, is_min)
    return heap


def random_invalid_heap(rng, n, is_min):
    """
    Start from a valid 1-indexed heap then swap a parent-child pair to
    introduce a violation. Retries until the violation is genuine.
    """
    arr = random_valid_heap(rng, n, is_min)
    end = len(arr) - 1
    for _ in range(40):
        parent   = rng.randint(1, end // 2)
        children = [c for c in (2 * parent, 2 * parent + 1) if c <= end]
        if not children:
            continue
        child = rng.choice(children)
        arr[parent], arr[child] = arr[child], arr[parent]
        if not is_valid_heap(arr, is_min):
            return arr
        arr[parent], arr[child] = arr[child], arr[parent]    # undo
    # Fallback: force root violation
    arr[1] = min(arr[1:]) if not is_min else max(arr[1:])
    return arr


# ─────────────────────────────────────────────
#  QUESTION GENERATORS
# ─────────────────────────────────────────────

def q_array_to_heap(rng):
    """Q1: Given a random array, build a Min or Max heap using Floyd's algorithm."""
    n      = rng.randint(6, 14)
    is_min = random_heap_type(rng)
    values = rng.sample(range(1, 100), n)

    # Show input as a plain array (0-based, no None yet — it's not a heap)
    plain_vals = '  [ ' + ', '.join(f'{v}' for v in values) + ' ]'
    plain_idxs = '    ' + '  '.join(f'{i}' for i in range(len(values)))

    print("\n" + "=" * 62)
    print(f"Q: Convert the following array into a {heap_label(is_min)}")
    print(f"   using Floyd's heapify (sift-down from index n//2 down to 1).")
    print(f"   Use 1-based indexing: prepend None at index 0 first.")
    print()
    print("  Input array (0-based, before conversion):")
    print(plain_vals)
    print(plain_idxs)
    print("=" * 62)

    def show_answer():
        heap, steps = build_heap_floyd(list(values), is_min)
        orig_1based = [None] + list(values)
        print("\n── ANSWER ──")
        print(f"\n  Step 0 — prepend None, reindex to 1-based:")
        print(f"  {_fmt_snap(orig_1based)}")
        idxs = '  ' + '  '.join(f'{i}' for i in range(len(orig_1based)))
        print(idxs)
        if steps:
            print(f"\n  Floyd sift-down steps (start at index n//2 = {len(values)//2}, go to 1):")
            for idx_a, idx_b, snap in steps:
                print(f"    swap idx {idx_a} ↔ idx {idx_b}  →  {_fmt_snap(snap)}")
        else:
            print("\n  No swaps needed — array is already a valid heap.")
        print(f"\n  Final {heap_label(is_min)}:")
        print_indexed_array(heap)
        print(f"\n  Tree view:")
        pretty_print_heap(heap)
        print()

    return show_answer


def q_is_valid_heap(rng):
    """Q2: Is this a valid Min or Max heap? Randomly shows array OR tree."""
    n         = rng.randint(6, 13)
    is_min    = random_heap_type(rng)
    valid     = rng.choice([True, False])
    arr       = (random_valid_heap(rng, n, is_min)
                 if valid else random_invalid_heap(rng, n, is_min))
    answer    = is_valid_heap(arr, is_min)
    show_tree = rng.choice([True, False])

    print("\n" + "=" * 62)
    fmt_hint = "(tree view)" if show_tree else "(array with indices)"
    print(f"Q: Is the following a valid {heap_label(is_min)}? {fmt_hint}  (Yes / No)")
    print(f"   (1-based: index 0 = None, root at index 1,")
    print(f"    parent(i) = i//2,  left = 2i,  right = 2i+1)")
    print()
    if show_tree:
        pretty_print_heap(arr)
    else:
        print_indexed_array(arr)
    print("=" * 62)

    def show_answer():
        print("\n── ANSWER ──")
        verdict = ('YES — Valid ' + heap_label(is_min) + '.'
                   if answer else 'NO — NOT a valid ' + heap_label(is_min) + '.')
        print(f"  {verdict}")
        violations = []
        end = len(arr) - 1
        for i in range(1, end + 1):
            for child in (2 * i, 2 * i + 1):
                if child <= end:
                    if not _cmp(arr[i], arr[child], is_min) and arr[i] != arr[child]:
                        violations.append((i, child, arr[i], arr[child]))
        if violations:
            op = '<' if is_min else '>'
            print(f"\n  Violations (parent must be {op} child):")
            for pi, ci, pv, cv in violations:
                print(f"    idx {pi} (val={pv})  vs  idx {ci} (val={cv})  ← VIOLATION")
        # Always show both representations in the answer
        print(f"\n  Full picture:")
        print_indexed_array(arr)
        pretty_print_heap(arr)
        print()

    return show_answer


def q_heap_to_array(rng):
    """Q3: Given a heap, extract elements to produce a sorted array."""
    n         = rng.randint(6, 12)
    is_min    = random_heap_type(rng)
    heap      = random_valid_heap(rng, n, is_min)
    direction = "ascending" if is_min else "descending"

    print("\n" + "=" * 62)
    print(f"Q: Given the following {heap_label(is_min)}, repeatedly extract")
    print(f"   the root to produce a {direction}-sorted array.")
    print(f"   (Swap root↔last, shrink heap by 1, sift root down, repeat.)")
    print(f"   (1-based: index 0 = None, root at index 1)")
    print()
    print_indexed_array(heap)
    print()
    pretty_print_heap(heap)
    print("=" * 62)

    def show_answer():
        sorted_vals, steps = heap_to_sorted_array(list(heap), is_min)
        print("\n── ANSWER ──")
        print(f"\n  Extraction steps:")
        for i, (val, remaining) in enumerate(steps, 1):
            if len(remaining) > 1:
                rem_str = _fmt_snap(remaining)
            else:
                rem_str = "[None]  (heap now empty)"
            print(f"    Step {i:>2}: extract {val:>2}  →  heap: {rem_str}")
        print(f"\n  Sorted output ({direction}): {sorted_vals}")
        print()

    return show_answer


def q_convert_heap(rng):
    """Q4: Convert a Min-heap to a Max-heap or vice versa.
    Question shows array only. First Enter reveals tree. Second Enter reveals answer."""
    n          = rng.randint(6, 13)
    src_is_min = random_heap_type(rng)
    src_heap   = random_valid_heap(rng, n, src_is_min)
    src_label  = heap_label(src_is_min)
    dst_label  = heap_label(not src_is_min)

    print("\n" + "=" * 62)
    print(f"Q: Convert the following {src_label} into a {dst_label}.")
    print(f"   (Apply Floyd's heapify with the opposite comparison.)")
    print(f"   (1-based: index 0 = None, root at index 1)")
    print()
    print(f"  Source {src_label} — array:")
    print_indexed_array(src_heap)
    print("=" * 62)

    def show_tree():
        print("\n── TREE VIEW ──")
        pretty_print_heap(src_heap)

    def show_answer():
        dst_heap, steps = convert_heap(list(src_heap), from_min_to_max=src_is_min)
        print("\n── ANSWER ──")
        if steps:
            print(f"\n  Floyd's sift-down steps for {dst_label}:")
            for idx_a, idx_b, snap in steps:
                print(f"    swap idx {idx_a} ↔ idx {idx_b}  →  {_fmt_snap(snap)}")
        else:
            print("  No swaps needed — source already satisfies the target heap property.")
        print(f"\n  Result {dst_label} — array:")
        print_indexed_array(dst_heap)
        print(f"\n  Result tree view:")
        pretty_print_heap(dst_heap)
        print()

    return show_tree, show_answer


# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────

QUESTIONS = [
    ("Array → Min/Max Heap  (Floyd's heapify)",     q_array_to_heap),
    ("Is it a valid Min/Max Heap?",                 q_is_valid_heap),
    ("Heap → Sorted array   (repeated extraction)", q_heap_to_array),
    ("Convert Min-Heap ↔ Max-Heap",                 q_convert_heap),
]


def print_menu():
    print("\n" + "╔" + "═" * 52 + "╗")
    print("║       HEAP EXAM PRACTICE — Choose a topic       ║")
    print("╠" + "═" * 52 + "╣")
    for i, (name, _) in enumerate(QUESTIONS, 1):
        print(f"║  [{i}] {name:<47}║")
    print("║  [5] Random question                             ║")
    print("║  [0] Quit                                        ║")
    print("╚" + "═" * 52 + "╝")
    print("Choice: ", end="", flush=True)


def main():
    rng = random.Random()    # seeded from system time → different each run

    print("\n🔺  Welcome to Heap Exam Practice  🔺")
    print("All heaps use 1-based indexing  (index 0 = None, root at index 1).")
    print("Each question prints first. Press ENTER to reveal the answer.")

    while True:
        print_menu()
        try:
            choice = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGood luck on your exam! 👍")
            break

        if choice == "0":
            print("\nGood luck on your exam! 👍\n")
            break

        if choice == "5":
            idx = rng.randint(0, len(QUESTIONS) - 1)
        elif choice.isdigit() and 1 <= int(choice) <= len(QUESTIONS):
            idx = int(choice) - 1
        else:
            print("  ⚠  Invalid choice. Please enter 0–5.")
            continue

        _, gen_fn = QUESTIONS[idx]
        result = gen_fn(rng)

        # q_convert_heap returns (show_tree, show_answer) — two-stage reveal
        if isinstance(result, tuple):
            show_tree, show_answer = result
            input("\n  [ Press ENTER to reveal the tree view ]")
            show_tree()
            input("\n  [ Press ENTER to reveal the answer ]")
            show_answer()
        else:
            show_answer = result
            input("\n  [ Press ENTER to reveal the answer ]")
            show_answer()

        input("  [ Press ENTER to return to menu ]")


if __name__ == "__main__":
    main()