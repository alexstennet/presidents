import numpy as np
import deepdish as dd

from helpers import hand_hash
from typing import Union

# hash table for identifying hands
hand_table = dd.io.load("hand_table.h5")

id_desc_dict = {
    0: "empty hand",  # i.e. [0, 0, 0, 0, 0]; should never persist
    11: "one card: single",  # e.g. [0, 0, 0, 0, 1]
    20: "two cards: invalid hand",  # e.g. [0, 0, 0, 1, 52]
    21: "two cards: double",  # e.g. [0, 0, 0, 1, 2]
    30: "three cards: invalid hand",  # e.g. [0, 0, 1, 2, 52]
    31: "three cards: triple",  # e.g. [0, 0, 1, 2, 3]
    40: "four cards: invalid hand",  # e.g. [0, 1, 2, 3, 4]
    50: "five cards: invalid hand",  # e.g. [1, 2, 3, 5, 52]
    51: "five cards: fullhouse",  # e.g. [1, 2, 3, 51, 52]
    52: "five cards: straight",  # e.g. [1, 5, 9, 13, 17]
    53: "five cards: bomb",  # e.g. [1, 49, 50, 51, 52]
}

# mapping from insertion index to appropriate invalid id
invalid_id_dict = {
    2: 20,
    3: 30,
    4: 40,
    5: 50,
}


class Hand:
    """
    Base class for president's hands and the core data structure of
    Presidents. Refactoring from original Hand class found in class
    Hand within spcl_presidents.py. Uses numpy arrays to represent
    hands.

    Right now, the way this is set up is for individual selection of
    cards in a gui where the player would click on a card to start
    building a hand and have the validity (whether it is a double, 
    triple, bomb, etc.) of the hand update dynamically.

    There will always be an empty hand and that hand can be put into 
    hand storage if it is a valid non single hand; once a hand is put
    into storage, a new empty hand will be created. Singles cannot be
    stored. If a single card is selected, all stored hands containing
    that card will be highlighted, signifying deletion of the stored
    hand if the single is played.
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

    # I have pretty much decided that all operations will be with base
    # python while the hand container is an uint8 np array because of a
    # smaller .tostring() -- ok so it seems like the uints are useless
    # lol

    def __init__(self, initial_card: int) -> None:
        """
        Hands always start out empty.
        """
        self._cards = np.zeros(shape=5, dtype=np.uint8)
        self._id = 0
        self._insertion_index = 4

    def __getitem__(self, key: Union[int, slice]) -> int:
        return self._cards[key]

    def __setitem__(self, key: Union[int, slice], value: int) -> None:
        self._cards[key] = value

    def __contains__(self, value: int) -> bool:
        return value in self._cards

    @property
    def _is_full(self) -> bool:
        return self._insertion_index == -1

    @property
    def _number_of_cards(self) -> int:
        return 4 - self._insertion_index

    def _identify(self) -> None:
        h = hash(self)
        if h not in hand_table:
            self._id = invalid_id_dict[self._number_of_cards]
        else:
            self._id = hand_table[h]

    def _add(self, card: int) -> None:
        assert 1 <= card <= 52, "Bug: attempting to add invalid card."
        assert card not in self, "Bug: attemping to add duplicate card."
        if (self._is_full):
            print("Cannot add any more cards to this hand.")
            return
        else:
            ii = self._insertion_index
            self[ii] = card
            self._add_sort(ii)
            self._insertion_index -= 1
        self._identify()

    def _add_sort(self, index: int) -> None:
        """
        Special sorting algorithm -- wow v algorithm
        runs in big omega 1, big o 4
        TODO: calculate average worst case runtimes with random
              insertions into hands with 1, 2, 3, and 4 cards in a
              jupyter notebook

              once I have actual user data, can also present average
              empirical runtimes.
        """
        i = index
        if i == 4:  # inserted card has reached the last index
            return
        elif self[i] > self[i + 1]:  # inserted card is greater than next
            self[i], self[i + 1] = self[i + 1], self[i]  # pythonic swap
            self._add_sort(i + 1)  # recurse on inserted card's new position
        else:  # inserted card is less than next, i.e. in the right position
            return

    def _card_index(self, card) -> int:
        assert (card in self,
                "Bug: attempting to find index of card which is not in hand.")
        return np.where(self._cards == card)[0][0]

    def _remove(self, card) -> None:
        assert self._id != 0, "Bug: attempting to remove from an empty hand."
        ci = self._card_index(card)
        self[ci] = 0
        self._insertion_index += 1
        self._remove_sort(ci)

    def _remove_sort(self, card_index: int) -> None:
        ci = card_index
        ii = self._insertion_index
        self[ii + 1: ci + 1] = self[ii: ci]
        self[ii] = 0

    @property
    def _id_desc(self) -> str:
        return id_desc_dict[self._id]

    def __repr__(self) -> str:
        return f"Hand({self._cards}; {self._id_desc})"

    def __hash__(self) -> int:
        return hand_hash(self._cards)
