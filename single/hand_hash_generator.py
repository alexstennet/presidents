import itertools
import numpy as np
from numba import jit
from numba import uint8

@jit(uint8(uint8[:]), nopython=True, nogil=True, parallel=True)
def hand_id(hand):
    """
    hand is a numpy array with length 5
    """
    # empty hand
    if hand[4] == 0:
        return np.uint8(0)

    # single
    elif (hand[3] == 0 and
          hand[4] != 0):

        return np.uint8(1)

    # double
    elif (hand[2] == 0 and
          hand[4] - hand[3] <= 3):

        return np.uint8(2)

    elif ()
