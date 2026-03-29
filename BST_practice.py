#!/usr/bin/env python3
"""
BST Exam Practice Tool
Generates random BST questions with deterministic logic via random library.
"""

import random
from collections import deque


# ─────────────────────────────────────────────
#  BST NODE & CORE OPERATIONS
# ─────────────────────────────────────────────

class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def insert_bst(root, val):
    """Standard BST insert."""
    if root is None:
        return Node(val)
    if val < root.val:
        root.left = insert_bst(root.left, val)
    else:
        root.right = insert_bst(root.right, val)
    return root


def build_bst_from_array(arr):
    """Build BST by inserting elements in order."""
    root = None
    for v in arr:
        root = insert_bst(root, v)
    return root


def inorder(root):
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


def preorder(root):
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)


def postorder(root):
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]


def level_order(root):
    if root is None:
        return []
    result, q = [], deque([root])
    while q:
        node = q.popleft()
        result.append(node.val)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
    return result


# ─────────────────────────────────────────────
#  TREE PROPERTY CHECKS
# ─────────────────────────────────────────────

def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    """Check if tree is a valid BST."""
    if root is None:
        return True
    if not (min_val < root.val < max_val):
        return False
    return (is_valid_bst(root.left, min_val, root.val) and
            is_valid_bst(root.right, root.val, max_val))


def tree_height(root):
    if root is None:
        return 0
    return 1 + max(tree_height(root.left), tree_height(root.right))


def is_balanced(root):
    """Check AVL-style balance: no subtree height differs by more than 1."""
    def check(node):
        if node is None:
            return 0
        lh = check(node.left)
        if lh == -1:
            return -1
        rh = check(node.right)
        if rh == -1:
            return -1
        if abs(lh - rh) > 1:
            return -1
        return 1 + max(lh, rh)
    return check(root) != -1


# ─────────────────────────────────────────────
#  PRETTY-PRINT BST
# ─────────────────────────────────────────────

def _display_aux(node):
    """
    Recursively compute a list of display lines for the subtree rooted at node.
    Returns: (lines, total_width, height, root_offset)
      - lines       : list of strings, each exactly total_width chars wide
      - total_width : character width of this subtree's block
      - height      : number of lines
      - root_offset : horizontal index (0-based) of the root character within lines[0]
    Adapted from the well-known Stack Overflow / LeetCode community algorithm.
    """
    label = str(node.val)
    w = len(label)

    # ── Leaf node ──
    if node.left is None and node.right is None:
        return [label], w, 1, w // 2

    # ── Only left child ──
    if node.right is None:
        left_lines, lw, lh, lx = _display_aux(node.left)
        # Root sits to the right of its left child's root
        first  = ' ' * (lx + 1) + '_' * (lw - lx - 1) + label
        second = ' ' * lx + '/' + ' ' * (lw - lx - 1 + w)
        pad    = [line + ' ' * w for line in left_lines]
        return [first, second] + pad, lw + w, lh + 2, lw + w // 2

    # ── Only right child ──
    if node.left is None:
        right_lines, rw, rh, rx = _display_aux(node.right)
        first  = label + '_' * rx + ' ' * (rw - rx)
        second = ' ' * (w + rx) + '\\' + ' ' * (rw - rx - 1)
        pad    = [' ' * w + line for line in right_lines]
        return [first, second] + pad, w + rw, rh + 2, w // 2

    # ── Both children ──
    left_lines,  lw, lh, lx = _display_aux(node.left)
    right_lines, rw, rh, rx = _display_aux(node.right)

    # The root label sits between the two subtrees with connecting underscores
    gap   = 1                           # minimum 1-space gap between subtrees
    total = lw + gap + rw
    root_pos = lw + gap // 2           # root is placed just after the left block

    first  = (' ' * (lx + 1)
              + '_' * (lw - lx - 1)
              + label
              + '_' * rx
              + ' ' * (rw - rx))
    second = (' ' * lx + '/'
              + ' ' * (lw - lx - 1 + w + rx)
              + '\\'
              + ' ' * (rw - rx - 1))

    # Pad shorter side so both reach the same height
    if lh < rh:
        left_lines  += [' ' * lw] * (rh - lh)
    elif rh < lh:
        right_lines += [' ' * rw] * (lh - rh)

    middle = [l + ' ' * (gap) + r for l, r in zip(left_lines, right_lines)]
    lines  = [first, second] + middle
    return lines, lw + w + rw, len(lines), lw + w // 2


def pretty_print_bst(root):
    """Print a BST with correctly positioned nodes and / \\ connectors."""
    if root is None:
        print("(empty tree)")
        return
    lines, _, _, _ = _display_aux(root)
    for line in lines:
        print(' ' + line)   # 1-space left margin for readability


# ─────────────────────────────────────────────
#  RECONSTRUCT BST FROM 2 TRAVERSALS
# ─────────────────────────────────────────────

def build_from_preorder_inorder(preord, inord):
    """Reconstruct BST from preorder + inorder."""
    if not preord or not inord:
        return None
    root_val = preord[0]
    root = Node(root_val)
    idx = inord.index(root_val)
    root.left = build_from_preorder_inorder(preord[1:1 + idx], inord[:idx])
    root.right = build_from_preorder_inorder(preord[1 + idx:], inord[idx + 1:])
    return root


def build_from_postorder_inorder(postord, inord):
    """Reconstruct BST from postorder + inorder."""
    if not postord or not inord:
        return None
    root_val = postord[-1]
    root = Node(root_val)
    idx = inord.index(root_val)
    root.left = build_from_postorder_inorder(postord[:idx], inord[:idx])
    root.right = build_from_postorder_inorder(postord[idx:-1], inord[idx + 1:])
    return root


def build_from_preorder_postorder(preord, postord):
    """Reconstruct a full BST from preorder + postorder (unique if full tree)."""
    if not preord:
        return None
    root = Node(preord[0])
    if len(preord) == 1:
        return root
    # Left subtree root is preord[1]; find it in postorder
    left_root_val = preord[1]
    left_size = postord.index(left_root_val) + 1
    root.left = build_from_preorder_postorder(preord[1:1 + left_size], postord[:left_size])
    root.right = build_from_preorder_postorder(preord[1 + left_size:], postord[left_size:-1])
    return root


# ─────────────────────────────────────────────
#  RANDOM TREE GENERATORS
# ─────────────────────────────────────────────

def random_bst(rng, n):
    """Generate a random BST with n distinct nodes (values 1–99)."""
    values = rng.sample(range(1, 100), n)
    insert_order = list(values)
    rng.shuffle(insert_order)
    root = None
    for v in insert_order:
        root = insert_bst(root, v)
    return root, sorted(values)


def random_valid_bst(rng, n):
    """Always returns a valid BST."""
    return random_bst(rng, n)


def random_invalid_bst(rng, n):
    """
    Build a valid BST then corrupt one node's value to violate BST property.
    Returns the corrupted tree as a Node structure.
    """
    root, _ = random_bst(rng, n)
    nodes = []

    def collect(node):
        if node:
            nodes.append(node)
            collect(node.left)
            collect(node.right)

    collect(root)

    # Pick a non-root node and corrupt its value
    # Try up to 20 times to find a corruption that actually breaks BST property
    for _ in range(20):
        target = rng.choice(nodes[1:]) if len(nodes) > 1 else nodes[0]
        all_vals = [nd.val for nd in nodes]
        # Pick a value that violates BST at this position
        bad_candidates = [v for v in range(1, 100)
                          if v not in all_vals and v != target.val]
        if not bad_candidates:
            continue
        bad_val = rng.choice(bad_candidates)
        original_val = target.val
        target.val = bad_val
        if not is_valid_bst(root):
            return root
        # Restore if it didn't break it
        target.val = original_val

    # Fallback: force an obvious violation on root's left child
    if root.left is not None:
        root.left.val = root.val + rng.randint(1, 10)
    else:
        root.right = Node(root.val - rng.randint(1, 10))
    return root


def random_unbalanced_bst(rng, n):
    """Build a BST guaranteed to be unbalanced by inserting in sorted order."""
    values = sorted(rng.sample(range(1, 100), n))
    root = None
    for v in values:
        root = insert_bst(root, v)
    return root, values


def make_balanced_bst(rng, n):
    """Build a balanced BST from a sorted array via mid-point insertion."""
    values = sorted(rng.sample(range(1, 100), n))

    def build(arr):
        if not arr:
            return None
        mid = len(arr) // 2
        node = Node(arr[mid])
        node.left = build(arr[:mid])
        node.right = build(arr[mid + 1:])
        return node

    return build(values), values


# ─────────────────────────────────────────────
#  QUESTION GENERATORS
# ─────────────────────────────────────────────

def q_two_traversals_to_bst(rng):
    """Q1: Given 2 traversals, reconstruct BST layout."""
    n = rng.randint(5, 12)
    root, _ = random_valid_bst(rng, n)

    traversal_pairs = [
        ("Inorder",   "Preorder",  inorder(root),   preorder(root)),
        ("Inorder",   "Postorder", inorder(root),   postorder(root)),
        ("Preorder",  "Postorder", preorder(root),  postorder(root)),
    ]
    choice = rng.choice(traversal_pairs)
    name1, name2, t1, t2 = choice

    print("\n" + "=" * 60)
    print("Q: Given the following two BST traversals, draw the BST layout.")
    print(f"\n  {name1}:  {t1}")
    print(f"  {name2}: {t2}")
    print("=" * 60)

    def show_answer():
        print("\n── ANSWER ──")
        # Reconstruct
        if name1 == "Inorder" and name2 == "Preorder":
            ans_root = build_from_preorder_inorder(t2, t1)
        elif name1 == "Inorder" and name2 == "Postorder":
            ans_root = build_from_postorder_inorder(t2, t1)
        else:  # Preorder + Postorder
            ans_root = build_from_preorder_postorder(t1, t2)
        pretty_print_bst(ans_root)
        print()

    return show_answer


def q_two_traversals_to_original(rng):
    """Q2: Given 2 traversals, find all traversals of the original tree."""
    n = rng.randint(5, 12)
    root, _ = random_valid_bst(rng, n)

    pre  = preorder(root)
    ino  = inorder(root)
    post = postorder(root)
    lvl  = level_order(root)

    # Hide one or two traversals, show the rest as clues
    all_traversals = [
        ("Inorder",      ino),
        ("Preorder",     pre),
        ("Postorder",    post),
        ("Level-order",  lvl),
    ]
    shown_indices = rng.sample(range(4), 2)
    shown = [all_traversals[i] for i in shown_indices]

    print("\n" + "=" * 60)
    print("Q: Reconstruct the original BST and list ALL traversals.")
    for name, trav in shown:
        print(f"\n  {name}:  {trav}")
    print("=" * 60)

    def show_answer():
        print("\n── ANSWER ──")
        print("BST Layout:")
        pretty_print_bst(root)
        print(f"\n  Inorder    : {ino}")
        print(f"  Preorder   : {pre}")
        print(f"  Postorder  : {post}")
        print(f"  Level-order: {lvl}")
        print()

    return show_answer


def q_is_valid_bst(rng):
    """Q3: Is this a valid BST?"""
    n = rng.randint(5, 10)
    make_valid = rng.choice([True, False])

    if make_valid:
        root, _ = random_valid_bst(rng, n)
    else:
        root = random_invalid_bst(rng, n)

    answer = is_valid_bst(root)

    print("\n" + "=" * 60)
    print("Q: Is the following tree a valid BST? (Yes / No)")
    pretty_print_bst(root)
    print("=" * 60)

    def show_answer():
        print("\n── ANSWER ──")
        print(f"  {'YES — It is a valid BST.' if answer else 'NO — It is NOT a valid BST.'}")
        if not answer:
            # Show what inorder looks like (should be sorted for valid BST)
            vals = []
            def collect_inorder(nd):
                if nd:
                    collect_inorder(nd.left)
                    vals.append(nd.val)
                    collect_inorder(nd.right)
            collect_inorder(root)
            print(f"  Inorder traversal: {vals}  ← not sorted, violates BST property")
        print()

    return show_answer


def q_is_balanced_bst(rng):
    """Q4: Is this a balanced BST?"""
    n = rng.randint(5, 12)
    make_balanced = rng.choice([True, False])

    if make_balanced:
        root, _ = make_balanced_bst(rng, n)
    else:
        root, _ = random_unbalanced_bst(rng, n)

    answer = is_balanced(root)

    print("\n" + "=" * 60)
    print("Q: Is the following BST balanced? (Yes / No)")
    pretty_print_bst(root)
    print("=" * 60)

    def show_answer():
        print("\n── ANSWER ──")
        print(f"  {'YES — The BST is balanced.' if answer else 'NO — The BST is NOT balanced.'}")

        # Show subtree heights for context
        def heights(node, depth=0, prefix="Root"):
            if node is None:
                return
            lh = tree_height(node.left)
            rh = tree_height(node.right)
            diff = abs(lh - rh)
            flag = " ← IMBALANCE HERE" if diff > 1 else ""
            print(f"  Node [{node.val:>2}]  left_height={lh}  right_height={rh}  diff={diff}{flag}")
            heights(node.left,  depth + 1, "L")
            heights(node.right, depth + 1, "R")

        print("\n  Height breakdown per node:")
        heights(root)
        print()

    return show_answer


def q_array_to_bst(rng):
    """Q5: Given an array, draw the BST (insert left to right)."""
    n = rng.randint(5, 12)
    values = rng.sample(range(1, 100), n)

    print("\n" + "=" * 60)
    print("Q: Insert the following array into a BST (left to right) and draw the result.")
    print(f"\n  Array: {values}")
    print("=" * 60)

    def show_answer():
        root = None
        steps = []
        for v in values:
            root = insert_bst(root, v)
            steps.append(v)

        print("\n── ANSWER ──")
        print(f"  Insertion order: {steps}")
        print("\n  Resulting BST:")
        pretty_print_bst(root)
        print(f"\n  Inorder (sorted check): {inorder(root)}")
        print()

    return show_answer


# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────

QUESTIONS = [
    ("Two traversals → BST layout",          q_two_traversals_to_bst),
    ("Two traversals → All traversals",       q_two_traversals_to_original),
    ("Is it a valid BST?",                    q_is_valid_bst),
    ("Is it a balanced BST?",                 q_is_balanced_bst),
    ("Array → BST layout",                    q_array_to_bst),
]


def print_menu():
    print("\n" + "╔" + "═" * 46 + "╗")
    print("║      BST EXAM PRACTICE — Choose a topic      ║")
    print("╠" + "═" * 46 + "╣")
    for i, (name, _) in enumerate(QUESTIONS, 1):
        print(f"║  [{i}] {name:<41}║")
    print("║  [6] Random question                         ║")
    print("║  [0] Quit                                    ║")
    print("╚" + "═" * 46 + "╝")
    print("Choice: ", end="", flush=True)


def main():
    rng = random.Random()  # seeded from system time → different each run

    print("\n🌳  Welcome to BST Exam Practice  🌳")
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

        if choice == "6":
            idx = rng.randint(0, len(QUESTIONS) - 1)
        elif choice.isdigit() and 1 <= int(choice) <= len(QUESTIONS):
            idx = int(choice) - 1
        else:
            print("  ⚠  Invalid choice. Please enter 0–6.")
            continue

        _, gen_fn = QUESTIONS[idx]
        show_answer = gen_fn(rng)

        input("\n  [ Press ENTER to reveal the answer ]")
        show_answer()

        input("  [ Press ENTER to return to menu ]")


if __name__ == "__main__":
    main()