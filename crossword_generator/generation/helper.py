"""Non-specific helper methods."""

def union(A, B):
    """Union of dictionaries/sets A, B, which have the same 'object structure'"""
    if isinstance(A, set) and isinstance(B, set):
        return A | B
    elif isinstance(A, dict) and isinstance(B, dict):
        return {k: union(A[k], B[k]) for k in A}
    else:
        raise ValueError('Inputs do not have the same object structure.')

def merge_sum(A: dict[int], B: dict[int]) -> dict[int]:
    """Sum of 'merged' dictionaries A, B."""
    return {k: A.get(k, 0) + B.get(k, 0) for k in set(A) | set(B)}