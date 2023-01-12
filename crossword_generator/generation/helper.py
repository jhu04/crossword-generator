"""Non-specific helper methods."""

def collapse(f):
    """Returns function that collapses binary operator f. TODO: clean code."""
    def helper(ls):
        res = ls[0]
        for i in range(1, len(ls)):
            res = f(res, ls[i])
        return res
    return helper

def union(A, B):
    """Union of dictionaries/sets A, B, which have the same 'object structure'"""
    if isinstance(A, set) and isinstance(B, set):
        return A | B
    elif isinstance(A, dict) and isinstance(B, dict):
        return {k: union(A[k], B[k]) for k in A}
    else:
        raise ValueError('Inputs do not have the same object structure.')