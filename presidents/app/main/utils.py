import inspect
import sys
import numpy as np
from json import loads
from itertools import accumulate, repeat, chain

from xxhash import xxh32


def hand_hash(hand: np.ndarray) -> int:
    """
    hand should be a uint8 np array
    """
    return xxh32(hand.tostring()).intdigest()

def hand_to_json

def json_to_hand(json_hand: str):
    hand_dict = loads()
    cards = 


def cartesian_product_pp(arrays):
    """
    adapted from https://stackoverflow.com/a/49445693/9578116
    """
    la = len(arrays)
    L = *map(len, arrays), la
    arr = np.empty(L, dtype=np.uint8)
    arrs = *accumulate(chain((arr,), repeat(0, la-1)), np.ndarray.__getitem__),
    idx = slice(None), *repeat(None, la-1)
    for i in range(la-1, 0, -1):
        arrs[i][..., i] = arrays[i][idx[:la-i]]
        arrs[i-1][1:] = arrs[i]
    arr[..., 0] = arrays[0][idx]
    return arr.reshape(-1, la)


def main(fn):
    """
    source: ucb.py found in any of the python project starter files from
            cs61a.org

    Call fn with command line arguments.  Used as a decorator.

    The main decorator marks the function that starts a program. For
    example,

    @main
    def my_run_function():
        # function body

    Use this instead of the typical __name__ == "__main__" predicate.
    """
    if inspect.stack()[1][0].f_locals['__name__'] == '__main__':
        args = sys.argv[1:]  # Discard the script name from command line
        fn(*args)  # Call the main function
    return fn
