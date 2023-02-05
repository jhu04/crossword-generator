"""Non-specific helper methods."""
import sys
import bson
import bson.json_util
from distutils.util import strtobool


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


def to_bson(obj):
    """
    Recursively converts obj to a dictionary representation.
    See https://stackoverflow.com/a/48413290.
    """
    return bson.json_util.loads(bson.json_util.dumps(obj, default=lambda o: o.__dict__))


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the assumed answer if the user just hits <Enter>.
              It must be "yes" (the default), "no" or None (meaning
              an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    See https://stackoverflow.com/a/3041990.
    """
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError(f"invalid default answer: '{default}'")

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return strtobool(default)
        else:
            try:
                return strtobool(choice)
            except ValueError:
                sys.stdout.write("Please respond with 'yes'/'y' or 'no'/'n'.\n")