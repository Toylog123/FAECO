"""Core metric helpers for FAECO experiments."""


def change_ratio(patch_size: int, original_gate_count: int) -> float:
    """Return the fraction of original gates changed by a patch."""
    if original_gate_count <= 0:
        raise ValueError("original_gate_count must be positive")
    if patch_size < 0:
        raise ValueError("patch_size must be non-negative")
    return patch_size / original_gate_count


def logic_level_reduction(before: int, after: int) -> int:
    """Return the logic-level improvement from before to after."""
    return before - after
