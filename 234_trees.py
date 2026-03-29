#!/usr/bin/env python3
"""
2-3-4 Tree Exam Practice Tool
Topics:
  1. Is it a valid 2-3-4 tree?        (Yes/No + identify violated rule)
  2. Array → 2-3-4 tree               (step-by-step insertions)
  3. 2-3-4 Tree → RB Tree             (structural conversion)
  4. Insert value                      (steps + final tree)
  5. Delete value                      (steps + final tree, mix of simple/edge cases)
  6. Search for value                  (trace search path)

Display: text-art trees, black edges / \\ solid, red edges // \\\\ doubled.
All randomness via random.Random — deterministic per seed.
"""

import random
from copy import deepcopy


# ═══════════════════════════════════════════════════════
#  2-3-4 TREE NODE
# ═══════════════════════════════════════════════════════

class Node234:
    """
    A node in a 2-3-4 tree.
    keys     : sorted list of 1-3 keys
    children : list of 2-4 child Node234 (empty list for leaf)
    """
    def __init__(self, keys=None, children=None):
        self.keys     = list(keys)     if keys     else []
        self.children = list(children) if children else []

    def is_leaf(self):
        return len(self.children) == 0

    def num_keys(self):
        return len(self.keys)

    def num_children(self):
        return len(self.children)

    def is_full(self):
        return len(self.keys) == 3

    def __repr__(self):
        return f"Node234(keys={self.keys})"


# ═══════════════════════════════════════════════════════
#  PRETTY-PRINTER FOR 2-3-4 TREES
# ═══════════════════════════════════════════════════════

def _node_label(node):
    """Format a node as a bracketed key string, e.g. [10|20|30]."""
    return '[' + '|'.join(str(k) for k in node.keys) + ']'


def _build_lines(node):
    """
    Recursively build display lines for a 2-3-4 subtree.
    Returns (lines, width, root_start, root_end) where:
      lines      : list of strings (all same width)
      width      : character width of this block
      root_start : start col of root label (inclusive)
      root_end   : end col of root label (exclusive)
    """
    label = _node_label(node)
    lw    = len(label)

    if node.is_leaf():
        return [label], lw, 0, lw

    # Recursively lay out children
    child_blocks = [_build_lines(c) for c in node.children]
    # Each block: (lines, width, rs, re)

    # Gap between children
    gap = 2
    total_child_width = sum(b[1] for b in child_blocks) + gap * (len(child_blocks) - 1)

    # The root label is centred over the children area
    # But we need to know where each child's root centre is
    # to draw connector lines

    # Compute x-offsets of each child block
    offsets = []
    x = 0
    for b in child_blocks:
        offsets.append(x)
        x += b[1] + gap

    total_width = max(total_child_width, lw)
    # If label wider than children, pad children area
    children_offset = 0
    if lw > total_child_width:
        children_offset = (lw - total_child_width) // 2
        offsets = [o + children_offset for o in offsets]
        total_width = lw

    # Root centre
    root_centre = (offsets[0] + child_blocks[0][1] // 2 +
                   offsets[-1] + (child_blocks[-1][2] + child_blocks[-1][3]) // 2) // 2
    # Place label so it is centred between first and last child centre
    first_child_cx = offsets[0] + (child_blocks[0][2] + child_blocks[0][3]) // 2
    last_child_cx  = offsets[-1] + (child_blocks[-1][2] + child_blocks[-1][3]) // 2
    label_start    = (first_child_cx + last_child_cx) // 2 - lw // 2
    label_start    = max(0, label_start)
    # Expand total width if label overhangs
    label_end      = label_start + lw
    if label_end > total_width:
        total_width = label_end

    # Pad everything to total_width
    def pad(s, w):
        return s + ' ' * (w - len(s))

    # Line 0: root label
    root_line = ' ' * label_start + label
    root_line = pad(root_line, total_width)

    # Line 1: connector line  (/  |  \)
    conn = [' '] * total_width
    for idx, (b, off) in enumerate(zip(child_blocks, offsets)):
        cx = off + (b[2] + b[3]) // 2   # child label centre
        rx = label_start + lw // 2       # root centre

        if cx < rx:
            conn[cx] = '/'
        elif cx > rx:
            conn[cx] = '\\'
        else:
            conn[cx] = '|'
    conn_line = ''.join(conn)

    # Child lines: interleave children side by side
    max_child_height = max(len(b[0]) for b in child_blocks)
    child_rows = []
    for row in range(max_child_height):
        line = [' '] * total_width
        for b, off in zip(child_blocks, offsets):
            if row < len(b[0]):
                s = b[0][row]
            else:
                s = ' ' * b[1]
            for j, ch in enumerate(s):
                if off + j < total_width:
                    line[off + j] = ch
        child_rows.append(''.join(line))

    lines = [root_line, conn_line] + child_rows
    # Normalise all lines to the same width
    lines = [pad(l, total_width) for l in lines]
    return lines, total_width, label_start, label_end


def pretty_print_234(root, indent=2):
    """Print a 2-3-4 tree as text art."""
    if root is None:
        print(' ' * indent + '(empty tree)')
        return
    lines, _, _, _ = _build_lines(root)
    for line in lines:
        print(' ' * indent + line)


# ═══════════════════════════════════════════════════════
#  2-3-4 TREE CORE OPERATIONS
# ═══════════════════════════════════════════════════════

def _split_child(parent, child_idx):
    """
    Split a full child (3 keys) of parent at child_idx.
    The middle key moves up to parent; left/right become two 2-nodes.
    Returns a log string describing the split.
    """
    child  = parent.children[child_idx]
    mid    = child.keys[1]
    left   = Node234([child.keys[0]],
                     child.children[:2] if not child.is_leaf() else [])
    right  = Node234([child.keys[2]],
                     child.children[2:] if not child.is_leaf() else [])
    parent.keys.insert(child_idx, mid)
    parent.children.pop(child_idx)
    parent.children.insert(child_idx,     right)
    parent.children.insert(child_idx,     left)
    return f"  split: pushed {mid} up to parent {parent.keys}"


def insert_234(root, key):
    """
    Insert key into a 2-3-4 tree using top-down splitting.
    Returns (new_root, steps) where steps is a list of strings.
    """
    steps = []

    # Special case: empty tree
    if root is None:
        steps.append(f"  tree empty → create root [{key}]")
        return Node234([key]), steps

    # If root is full, split it first
    if root.is_full():
        new_root = Node234([root.keys[1]])
        left     = Node234([root.keys[0]],
                            root.children[:2] if not root.is_leaf() else [])
        right    = Node234([root.keys[2]],
                            root.children[2:] if not root.is_leaf() else [])
        new_root.children = [left, right]
        steps.append(f"  root full → split root, new root [{root.keys[1]}]")
        root = new_root

    # Walk down, splitting full nodes on the way
    node = root
    while not node.is_leaf():
        # Find which child to descend into
        ci = 0
        while ci < node.num_keys() and key > node.keys[ci]:
            ci += 1
        if key in node.keys:
            steps.append(f"  key {key} already exists — skipping")
            return root, steps
        child = node.children[ci]
        if child.is_full():
            msg = _split_child(node, ci)
            steps.append(msg)
            # Recompute index after split
            ci = 0
            while ci < node.num_keys() and key > node.keys[ci]:
                ci += 1
            if key in node.keys:
                steps.append(f"  key {key} is the split median — done")
                return root, steps
        node = node.children[ci]

    # Insert into leaf
    if key not in node.keys:
        node.keys.append(key)
        node.keys.sort()
        steps.append(f"  insert {key} into leaf → {node.keys}")
    else:
        steps.append(f"  key {key} already exists in leaf — skipping")
    return root, steps


def search_234(root, key):
    """
    Search for key in the tree.
    Returns list of step strings describing the path.
    """
    steps = []
    node  = root
    depth = 0
    while node is not None:
        label = _node_label(node)
        steps.append(f"  level {depth}: visit {label}")
        if key in node.keys:
            steps.append(f"  → FOUND {key} in {label}")
            return True, steps
        # Determine which child to follow
        ci = 0
        while ci < node.num_keys() and key > node.keys[ci]:
            ci += 1
        if node.is_leaf():
            steps.append(f"  → NOT FOUND (reached leaf, no children)")
            return False, steps
        steps.append(f"  → descend to child {ci}")
        node  = node.children[ci]
        depth += 1
    steps.append(f"  → NOT FOUND")
    return False, steps


# ── Delete helpers ──────────────────────────────────────

def _find_min_leaf(node):
    """Return the in-order successor (leftmost key in subtree)."""
    while not node.is_leaf():
        node = node.children[0]
    return node.keys[0]


def _transfer_from_right(parent, ci, steps):
    """Transfer: borrow from right sibling via parent."""
    node    = parent.children[ci]
    sibling = parent.children[ci + 1]
    node.keys.append(parent.keys[ci])
    parent.keys[ci] = sibling.keys.pop(0)
    if not sibling.is_leaf():
        node.children.append(sibling.children.pop(0))
    steps.append(f"  transfer: borrowed {node.keys[-1]} from right sibling via parent")


def _transfer_from_left(parent, ci, steps):
    """Transfer: borrow from left sibling via parent."""
    node    = parent.children[ci]
    sibling = parent.children[ci - 1]
    node.keys.insert(0, parent.keys[ci - 1])
    parent.keys[ci - 1] = sibling.keys.pop()
    if not sibling.is_leaf():
        node.children.insert(0, sibling.children.pop())
    steps.append(f"  transfer: borrowed {node.keys[0]} from left sibling via parent")


def _fuse(parent, ci, steps):
    """
    Fuse: merge child[ci], parent.keys[ci], child[ci+1] into one node.
    Removes parent.keys[ci] and child[ci+1].
    Returns the merged node.
    """
    left    = parent.children[ci]
    right   = parent.children[ci + 1]
    mid_key = parent.keys.pop(ci)
    parent.children.pop(ci + 1)
    left.keys   = left.keys + [mid_key] + right.keys
    left.children = left.children + right.children
    steps.append(f"  fuse: merged [{mid_key}] with siblings → {left.keys}")
    return left


def _ensure_not_minimum(parent, ci, steps):
    """
    Before descending into child[ci], ensure it has > 1 key.
    Tries transfer from siblings first, then fuse.
    Returns updated ci (fuse may shift index).
    """
    child = parent.children[ci]
    if child.num_keys() > 1:
        return ci   # already fine

    # Try transfer from right sibling
    if ci + 1 < parent.num_children() and parent.children[ci + 1].num_keys() > 1:
        _transfer_from_right(parent, ci, steps)
        return ci

    # Try transfer from left sibling
    if ci - 1 >= 0 and parent.children[ci - 1].num_keys() > 1:
        _transfer_from_left(parent, ci, steps)
        return ci

    # Fuse: prefer fusing with right sibling if available
    if ci + 1 < parent.num_children():
        _fuse(parent, ci, steps)
        return ci
    else:
        _fuse(parent, ci - 1, steps)
        return ci - 1


def _delete_recursive(node, key, steps):
    """Recursively delete key from subtree rooted at node (node always has >1 key or is root)."""
    # Is key in this node?
    if key in node.keys:
        ki = node.keys.index(key)
        if node.is_leaf():
            node.keys.remove(key)
            steps.append(f"  delete {key} from leaf → {node.keys}")
        else:
            # Internal node: ensure right child can accept a deletion first
            ci = ki + 1
            ci = _ensure_not_minimum(node, ci, steps)
            # After restructuring, ki may have shifted if a fuse consumed it
            if key not in node.keys:
                # key was pulled into the fused child — recurse there
                _delete_recursive(node.children[ci], key, steps)
                return
            ki = node.keys.index(key)
            # Now find the in-order successor in the (possibly restructured) subtree
            succ = _find_min_leaf(node.children[ki + 1])
            steps.append(f"  {key} is internal — replace with in-order successor {succ}")
            node.keys[ki] = succ
            _delete_recursive(node.children[ki + 1], succ, steps)
    else:
        # Key not here — descend
        ci = 0
        while ci < node.num_keys() and key > node.keys[ci]:
            ci += 1
        if node.is_leaf():
            steps.append(f"  {key} not found in tree — nothing to delete")
            return
        ci = _ensure_not_minimum(node, ci, steps)
        _delete_recursive(node.children[ci], key, steps)


def delete_234(root, key):
    """
    Delete key from a 2-3-4 tree.
    Returns (new_root, steps).
    """
    steps = []
    if root is None:
        steps.append("  tree is empty — nothing to delete")
        return root, steps

    steps.append(f"  deleting {key} from tree")
    _delete_recursive(root, key, steps)

    # If root is now empty, shrink or remove
    if root.num_keys() == 0:
        if root.is_leaf():
            root = None
            steps.append("  root emptied — tree is now empty")
        else:
            root = root.children[0]
            steps.append("  root emptied — child becomes new root")

    return root, steps


# ═══════════════════════════════════════════════════════
#  VALIDATION
# ═══════════════════════════════════════════════════════

def validate_234(root):
    """
    Validate a 2-3-4 tree.
    Returns (is_valid, list_of_violations).
    Each violation is a human-readable string.
    """
    violations = []

    def _check(node, min_key, max_key, depth, leaf_depth_ref):
        if node is None:
            return

        # Rule 1: 1-3 keys per node
        if not (1 <= node.num_keys() <= 3):
            violations.append(
                f"Node {node.keys}: has {node.num_keys()} keys "
                f"(must be 1–3)"
            )

        # Rule 2: keys sorted
        for i in range(len(node.keys) - 1):
            if node.keys[i] >= node.keys[i + 1]:
                violations.append(
                    f"Node {node.keys}: keys not strictly ascending"
                )

        # Rule 3: key range (BST property)
        for k in node.keys:
            if min_key is not None and k <= min_key:
                violations.append(
                    f"Node {node.keys}: key {k} violates BST property "
                    f"(should be > {min_key})"
                )
            if max_key is not None and k >= max_key:
                violations.append(
                    f"Node {node.keys}: key {k} violates BST property "
                    f"(should be < {max_key})"
                )

        # Rule 4: correct child count
        if not node.is_leaf():
            expected = node.num_keys() + 1
            if node.num_children() != expected:
                violations.append(
                    f"Node {node.keys}: has {node.num_children()} children "
                    f"(expected {expected} for {node.num_keys()} keys)"
                )

        # Rule 5: all leaves at same depth
        if node.is_leaf():
            if leaf_depth_ref[0] is None:
                leaf_depth_ref[0] = depth
            elif depth != leaf_depth_ref[0]:
                violations.append(
                    f"Node {node.keys}: leaf at depth {depth}, "
                    f"but first leaf found at depth {leaf_depth_ref[0]} "
                    f"(all leaves must be at same depth)"
                )
            return

        # Recurse into children
        bounds = ([None] + node.keys, node.keys + [None])
        for i, child in enumerate(node.children):
            lo = node.keys[i - 1] if i > 0 else min_key
            hi = node.keys[i]     if i < node.num_keys() else max_key
            _check(child, lo, hi, depth + 1, leaf_depth_ref)

    leaf_depth_ref = [None]
    _check(root, None, None, 0, leaf_depth_ref)
    return len(violations) == 0, violations


# ═══════════════════════════════════════════════════════
#  2-3-4 → RED-BLACK TREE CONVERSION
# ═══════════════════════════════════════════════════════

class RBNode:
    """Red-Black tree node."""
    def __init__(self, key, color='B', left=None, right=None, parent=None):
        self.key    = key
        self.color  = color   # 'R' or 'B'
        self.left   = left
        self.right  = right
        self.parent = parent

    def __repr__(self):
        return f"RBNode({self.key},{self.color})"


def _234_to_rb(node234):
    """
    Convert a 2-3-4 tree node to a red-black subtree.
    Rules:
      2-node [a]        → Black node a
      3-node [a|b]      → Black b, Red left child a  (left-leaning)
      4-node [a|b|c]    → Black b, Red left child a, Red right child c
    Children of the 2-3-4 node become children of the appropriate RB nodes.
    """
    if node234 is None:
        return None

    keys = node234.keys
    ch   = node234.children   # 0-4 children

    def child_rb(i):
        """Convert i-th child of the 2-3-4 node, or None if leaf."""
        if node234.is_leaf():
            return None
        return _234_to_rb(ch[i])

    if len(keys) == 1:
        # 2-node: single black node
        rb         = RBNode(keys[0], 'B')
        rb.left    = child_rb(0)
        rb.right   = child_rb(1)
        return rb

    elif len(keys) == 2:
        # 3-node: black right (b), red left child (a) — left-leaning
        rb_b       = RBNode(keys[1], 'B')
        rb_a       = RBNode(keys[0], 'R')
        rb_a.left  = child_rb(0)
        rb_a.right = child_rb(1)
        rb_b.left  = rb_a
        rb_b.right = child_rb(2)
        return rb_b

    else:
        # 4-node: black middle (b), red left (a), red right (c)
        rb_b        = RBNode(keys[1], 'B')
        rb_a        = RBNode(keys[0], 'R')
        rb_c        = RBNode(keys[2], 'R')
        rb_a.left   = child_rb(0)
        rb_a.right  = child_rb(1)
        rb_c.left   = child_rb(2)
        rb_c.right  = child_rb(3)
        rb_b.left   = rb_a
        rb_b.right  = rb_c
        return rb_b


def convert_to_rb(root234):
    """Convert a full 2-3-4 tree to a Red-Black tree. Returns RBNode root."""
    return _234_to_rb(root234)


# ── RB Tree pretty-printer ────────────────────────────

def _rb_display_aux(node):
    """
    Build display lines for an RB subtree.
    Black edges: / and \\
    Red edges:   // and \\\\  (doubled)
    Returns (lines, width, root_offset).
    """
    if node is None:
        return [], 0, 0, 0

    label = f"[{node.key}]"
    w     = len(label)

    def edge_chars(child_color):
        """Return (left_edge, right_edge) strings based on child's color."""
        if child_color == 'R':
            return '//', '\\\\'
        return '/', '\\'

    left_lines  = right_lines  = []
    lw = rw = lx = rx = 0

    if node.left is not None:
        left_lines, lw, lh, lx = _rb_display_aux(node.left)
    if node.right is not None:
        right_lines, rw, rh, rx = _rb_display_aux(node.right)

    # Leaf
    if node.left is None and node.right is None:
        return [label], w, 1, w // 2

    # Only left child
    if node.right is None:
        left_lines, lw, lh, lx = _rb_display_aux(node.left)
        le, _ = edge_chars(node.left.color)
        ew    = len(le)
        first  = ' ' * (lx + ew) + '_' * (lw - lx - ew) + label
        second = ' ' * lx + le + ' ' * (lw - lx - ew + w)
        pad    = [line + ' ' * w for line in left_lines]
        return [first, second] + pad, lw + w, lh + 2, lw + w // 2

    # Only right child
    if node.left is None:
        right_lines, rw, rh, rx = _rb_display_aux(node.right)
        _, re = edge_chars(node.right.color)
        ew    = len(re)
        first  = label + '_' * rx + ' ' * (rw - rx)
        second = ' ' * (w + rx) + re + ' ' * (rw - rx - ew)
        pad    = [' ' * w + line for line in right_lines]
        return [first, second] + pad, w + rw, rh + 2, w // 2

    # Both children
    left_lines,  lw, lh, lx = _rb_display_aux(node.left)
    right_lines, rw, rh, rx = _rb_display_aux(node.right)
    le, _ = edge_chars(node.left.color)
    _, re  = edge_chars(node.right.color)
    lew, rew = len(le), len(re)

    first  = (' ' * (lx + lew)
              + '_' * (lw - lx - lew)
              + label
              + '_' * rx
              + ' ' * (rw - rx))
    second = (' ' * lx + le
              + ' ' * (lw - lx - lew + w + rx)
              + re
              + ' ' * (rw - rx - rew))

    if lh < rh:
        left_lines  += [' ' * lw] * (rh - lh)
    elif rh < lh:
        right_lines += [' ' * rw] * (lh - rh)

    middle = [l + ' ' + r for l, r in zip(left_lines, right_lines)]
    lines  = [first, second] + middle
    return lines, lw + w + rw, len(lines), lw + w // 2


def pretty_print_rb(root, indent=2):
    """Print an RB tree. Black edges: / \\  Red edges: // \\\\"""
    if root is None:
        print(' ' * indent + '(empty tree)')
        return
    lines, _, _, _ = _rb_display_aux(root)
    for line in lines:
        print(' ' * indent + line)
    print()
    print(' ' * indent + 'Edge legend:  /  \\  = black edge    //  \\\\\\\\  = red edge')


# ═══════════════════════════════════════════════════════
#  RANDOM 2-3-4 TREE GENERATORS
# ═══════════════════════════════════════════════════════

def build_234_from_list(values):
    """Build a 2-3-4 tree by inserting values in order. Returns root."""
    root = None
    for v in values:
        root, _ = insert_234(root, v)
    return root


def random_valid_234(rng, n):
    """Build a valid 2-3-4 tree with n distinct keys."""
    values = rng.sample(range(1, 150), n)
    rng.shuffle(values)
    return build_234_from_list(values), sorted(values)


def random_invalid_234(rng, n):
    """
    Build a valid tree then corrupt it with one of several violations:
      V1 — overfull node (4 keys)
      V2 — unsorted keys in a node
      V3 — wrong child count
      V4 — unequal leaf depths
    Returns (root, violation_description).
    """
    root, _ = random_valid_234(rng, n)

    # Collect all nodes
    nodes = []
    def collect(nd):
        if nd:
            nodes.append(nd)
            for c in nd.children:
                collect(c)
    collect(root)

    violation_type = rng.choice(['overfull', 'unsorted', 'bad_child_count', 'unequal_depth'])

    if violation_type == 'overfull':
        target = rng.choice(nodes)
        extra  = rng.choice([k for k in range(1, 150) if k not in target.keys])
        target.keys.append(extra)
        target.keys.sort()
        return root, (f"Node {target.keys} has 4 keys (max is 3 — "
                      f"nodes must have 1–3 keys)")

    elif violation_type == 'unsorted':
        # Find a node with >= 2 keys to swap
        candidates = [nd for nd in nodes if nd.num_keys() >= 2]
        if not candidates:
            # fallback
            return random_invalid_234(rng, n)
        target = rng.choice(candidates)
        i = rng.randint(0, len(target.keys) - 2)
        target.keys[i], target.keys[i + 1] = target.keys[i + 1], target.keys[i]
        return root, (f"Node {target.keys}: keys are not in ascending order")

    elif violation_type == 'bad_child_count':
        # Find an internal node and remove one child
        internals = [nd for nd in nodes if not nd.is_leaf() and nd.num_children() > 2]
        if not internals:
            return random_invalid_234(rng, n)
        target = rng.choice(internals)
        target.children.pop()
        return root, (f"Node {target.keys}: has {target.num_children()} children "
                      f"(expected {target.num_keys() + 1})")

    else:  # unequal_depth
        # Find a leaf and attach a dummy child to make it internal with unequal depth
        leaves = [nd for nd in nodes if nd.is_leaf()]
        if not leaves:
            return random_invalid_234(rng, n)
        target = rng.choice(leaves)
        dummy_key = rng.choice([k for k in range(1, 150) if k not in target.keys])
        # Add exactly num_keys+1 children so only the depth property is violated
        for i in range(target.num_keys() + 1):
            target.children.append(Node234([dummy_key + i]))
        return root, (f"Node {target.keys}: is a leaf at one depth but has a child, "
                      f"violating the equal-leaf-depth property")


# ═══════════════════════════════════════════════════════
#  QUESTION GENERATORS
# ═══════════════════════════════════════════════════════

def q_is_valid_234(rng):
    """Q1: Is this a valid 2-3-4 tree? Yes/No + identify violation."""
    n     = rng.randint(7, 18)
    valid = rng.choice([True, False])

    if valid:
        root, _  = random_valid_234(rng, n)
        violation = None
    else:
        root, violation = random_invalid_234(rng, n)

    print("\n" + "=" * 64)
    print("Q: Is the following a valid 2-3-4 tree? (Yes / No)")
    print("   If No, identify which property is violated.")
    print()
    pretty_print_234(root)
    print("=" * 64)

    def show_answer():
        is_v, viols = validate_234(root)
        print("\n── ANSWER ──")
        if is_v:
            print("  YES — This is a valid 2-3-4 tree.")
            print("  All properties satisfied:")
            print("    ✓ Every node has 1–3 keys")
            print("    ✓ Keys within each node are sorted")
            print("    ✓ Every internal node with k keys has exactly k+1 children")
            print("    ✓ BST ordering property holds throughout")
            print("    ✓ All leaves are at the same depth")
        else:
            print("  NO — This is NOT a valid 2-3-4 tree.")
            print("  Violated rule(s):")
            for v in viols:
                print(f"    ✗ {v}")
        print()

    return show_answer


def q_array_to_234(rng):
    """Q2: Insert array values into a 2-3-4 tree one by one."""
    n      = rng.randint(6, 14)
    values = rng.sample(range(1, 100), n)

    print("\n" + "=" * 64)
    print("Q: Insert the following values into an empty 2-3-4 tree")
    print("   one by one (left to right). Show the final tree.")
    print(f"\n  Array: {values}")
    print("=" * 64)

    def show_answer():
        root = None
        all_steps = []
        for v in values:
            old_root = deepcopy(root)
            root, steps = insert_234(root, v)
            all_steps.append((v, steps, deepcopy(root)))

        print("\n── ANSWER ──")
        print(f"\n  Insertion trace:")
        for v, steps, snap in all_steps:
            print(f"\n  Insert {v}:")
            for s in steps:
                print(f"  {s}")
            pretty_print_234(snap)

        print(f"\n  Final tree:")
        pretty_print_234(root)
        print()

    return show_answer


def q_234_to_rb(rng):
    """Q3: Convert a 2-3-4 tree to a Red-Black tree."""
    n    = rng.randint(6, 15)
    root, _ = random_valid_234(rng, n)

    print("\n" + "=" * 64)
    print("Q: Convert the following 2-3-4 tree to a Red-Black tree.")
    print("   Rules: 2-node→black node; 3-node→black+red-left child;")
    print("          4-node→black middle + red left + red right children.")
    print()
    pretty_print_234(root)
    print("=" * 64)

    def show_answer():
        rb_root = convert_to_rb(root)
        print("\n── ANSWER ──")
        print("  Conversion rules applied per node:")
        print("    2-node [a]      → ●a  (black)")
        print("    3-node [a|b]    → ●b with ○a as left child  (left-leaning)")
        print("    4-node [a|b|c]  → ●b with ○a left, ○c right")
        print()
        print("  Resulting Red-Black Tree:")
        print("  (/ \\  = black edge,   //  \\\\\\\\  = red edge)")
        print()
        pretty_print_rb(rb_root)
        print()

    return show_answer


def q_insert_234(rng):
    """Q4: Insert a value into a 2-3-4 tree, show splits and final tree."""
    n    = rng.randint(6, 15)
    root, existing = random_valid_234(rng, n)
    # Pick a value not in the tree
    candidates = [k for k in range(1, 150) if k not in existing]
    new_val    = rng.choice(candidates)

    print("\n" + "=" * 64)
    print(f"Q: Insert {new_val} into the following 2-3-4 tree.")
    print("   Show all splits that occur and the final tree.")
    print()
    pretty_print_234(root)
    print("=" * 64)

    def show_answer():
        root_copy      = deepcopy(root)
        new_root, steps = insert_234(root_copy, new_val)
        print("\n── ANSWER ──")
        print(f"\n  Steps for inserting {new_val}:")
        for s in steps:
            print(f"  {s}")
        print(f"\n  Final tree after inserting {new_val}:")
        pretty_print_234(new_root)
        print()

    return show_answer


def q_delete_234(rng):
    """Q5: Delete a value from a 2-3-4 tree (mix of simple/edge cases)."""
    n    = rng.randint(8, 18)
    root, existing = random_valid_234(rng, n)

    # Choose deletion target — bias toward internal nodes for edge cases
    all_nodes = []
    def collect_keys(nd):
        if nd:
            for k in nd.keys:
                all_nodes.append((k, not nd.is_leaf()))
            for c in nd.children:
                collect_keys(c)
    collect_keys(root)

    # 60% chance to pick an internal node key (forces successor replacement)
    internal_keys = [k for k, is_int in all_nodes if is_int]
    leaf_keys     = [k for k, is_int in all_nodes if not is_int]

    if internal_keys and rng.random() < 0.6:
        del_val = rng.choice(internal_keys)
        case    = "internal node"
    elif leaf_keys:
        del_val = rng.choice(leaf_keys)
        case    = "leaf node"
    else:
        del_val = rng.choice(existing)
        case    = "node"

    print("\n" + "=" * 64)
    print(f"Q: Delete {del_val} from the following 2-3-4 tree.")
    print("   Show all transfers/fuses and the final tree.")
    print()
    pretty_print_234(root)
    print("=" * 64)

    def show_answer():
        root_copy      = deepcopy(root)
        new_root, steps = delete_234(root_copy, del_val)
        print("\n── ANSWER ──")
        print(f"\n  Steps for deleting {del_val} ({case}):")
        for s in steps:
            print(f"  {s}")
        print(f"\n  Final tree after deleting {del_val}:")
        pretty_print_234(new_root)
        print()

    return show_answer


def q_search_234(rng):
    """Q6: Trace the search path for a value in a 2-3-4 tree."""
    n    = rng.randint(7, 18)
    root, existing = random_valid_234(rng, n)

    # 50/50 — search for existing vs missing key
    if rng.choice([True, False]):
        target  = rng.choice(existing)
        present = True
    else:
        missing = [k for k in range(1, 150) if k not in existing]
        target  = rng.choice(missing)
        present = False

    print("\n" + "=" * 64)
    print(f"Q: Search for {target} in the following 2-3-4 tree.")
    print("   Trace the path taken. Is it found?")
    print()
    pretty_print_234(root)
    print("=" * 64)

    def show_answer():
        found, steps = search_234(root, target)
        print("\n── ANSWER ──")
        print(f"\n  Search trace for {target}:")
        for s in steps:
            print(f"  {s}")
        outcome = "FOUND" if found else "NOT FOUND"
        print(f"\n  Result: {target} is {outcome} in the tree.")
        print()

    return show_answer


# ═══════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════

QUESTIONS = [
    ("Is it a valid 2-3-4 tree?",              q_is_valid_234),
    ("Array → 2-3-4 tree",                     q_array_to_234),
    ("2-3-4 Tree → Red-Black Tree",            q_234_to_rb),
    ("Insert value into 2-3-4 tree",           q_insert_234),
    ("Delete value from 2-3-4 tree",           q_delete_234),
    ("Search for value in 2-3-4 tree",         q_search_234),
]


def print_menu():
    w = 56
    print("\n" + "╔" + "═" * w + "╗")
    print("║" + "    2-3-4 TREE EXAM PRACTICE — Choose a topic    ".center(w) + "║")
    print("╠" + "═" * w + "╣")
    for i, (name, _) in enumerate(QUESTIONS, 1):
        print(f"║  [{i}] {name:<{w-6}}║")
    print(f"║  [7] Random question{' ' * (w - 21)}║")
    print(f"║  [0] Quit{' ' * (w - 10)}║")
    print("╚" + "═" * w + "╝")
    print("Choice: ", end="", flush=True)


def main():
    rng = random.Random()

    print("\n🌲  Welcome to 2-3-4 Tree Exam Practice  🌲")
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

        if choice == "7":
            idx = rng.randint(0, len(QUESTIONS) - 1)
        elif choice.isdigit() and 1 <= int(choice) <= len(QUESTIONS):
            idx = int(choice) - 1
        else:
            print(f"  ⚠  Invalid choice. Please enter 0–7.")
            continue

        _, gen_fn = QUESTIONS[idx]
        show_answer = gen_fn(rng)

        input("\n  [ Press ENTER to reveal the answer ]")
        show_answer()
        input("  [ Press ENTER to return to menu ]")


if __name__ == "__main__":
    main()