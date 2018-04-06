import inspect
import sys
import numpy as np
from xxhash import xxh32


def hand_hash(hand: np.ndarray) -> int:
    """
    hand should be a uint8 np array
    """
    return xxh32(hand.tostring()).intdigest()


def main(fn):
    """Call fn with command line arguments.  Used as a decorator.

    The main decorator marks the function that starts a program. For example,

    @main
    def my_run_function():
        # function body

    Use this instead of the typical __name__ == "__main__" predicate.
    """
    if inspect.stack()[1][0].f_locals['__name__'] == '__main__':
        args = sys.argv[1:]  # Discard the script name from command line
        fn(*args)  # Call the main function
    return fn
