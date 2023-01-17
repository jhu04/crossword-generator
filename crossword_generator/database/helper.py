"""Non-specific helper methods."""
import sys
import bson
import bson.json_util
from distutils.util import strtobool


def to_bson(obj):
    """Recursively converts this document to a dictionary representation.

    See https://stackoverflow.com/a/48413290 for implementation details.

    Args:
        obj: the object to be recursively represented as a dictionary

    Returns:
        A dictionary representation of this object.
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