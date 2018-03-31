import numpy as np
from numba import jitclass
from numba import uint8

# jitclass specification
spec = [
    ('cards', uint8[:]),
    ('combo', uint8)
]

# hash table for identifying combos
combo_dict = 0

combo_ids = dict(
    np.arange(0, 7, dtype=np.uint8),
    {"not a valid combo", "single", "double", "triple", "fullhouse",
     "straight", "bomb"}
)


@jitclass(spec)
class Hand:
    """
    Base class for president's hands and the core data structure of
    Presidents. Refactoring from original Hand class found in class
    Hand. Uses uint8 numpy arrays to represent hands.
    """

    # cards are numbered 1-52

    # hand is initially populated with 0's sorted after every operation
    # and hashed for possible combo

    # hand is an int8 numpy array

    # not sure where to put support for being able to have more than 5
    # cards selected in a sort of queue? not sure this should even be
    # allowed since like if you have seven cards selected and then
    # remove one of the cards that was actually in the deck are the
    # queued cards added in order like honestly just don't like the idea
    # and will most likely just prevent it

    def __init__(self):
        self.cards = np.zeros(shape=5, dtype=np.uint8)
        # 0 is no combo, 1 is single, 2 is double, 3 is triple, 4 is
        # full house, 5 is straight, 6 is bomb
        self.combo = np.uint8(0)

    def __getitem__(self, key):
        return self.cards[key]

    def add(self, card):
        assert 1 <= card <= 52, "Bug: attempting to add invalid card."
        if (self[0] != 0):
            print("Hand is full.")
            return
        else:
            self[0] = card
            self.sort()

    def sort(self):
        self.cards.sort()
