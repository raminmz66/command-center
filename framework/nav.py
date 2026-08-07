"""Keyboard highlight index math for command cards."""


def next_highlight_index(current, key, n, columns=3):
    """Return next highlight index for arrow navigation.

    current: int or None (no highlight yet)
    key: "Left" | "Right" | "Up" | "Down"
    n: number of navigable cards
    columns: grid column count for vertical moves
    """
    if n <= 0:
        return None
    if current is None:
        if key in ("Up", "Left"):
            return n - 1
        return 0
    if key == "Right":
        return min(current + 1, n - 1)
    if key == "Left":
        return max(current - 1, 0)
    if key == "Down":
        return min(current + columns, n - 1)
    if key == "Up":
        return max(current - columns, 0)
    return current
