import numpy as np
import deepdish as dd

from utils import hand_hash
from typing import Union
from mypy_extensions import NoReturn

# hash table for identifying hands
hand_table = dd.io.load("hand_table.h5")

id_desc_dict = {
    0: "empty hand",  # i.e. [0, 0, 0, 0, 0]
    11: "single",  # e.g. [0, 0, 0, 0, 1]
    20: "invalid hand (2)",  # e.g. [0, 0, 0, 1, 52]
    21: "double",  # e.g. [0, 0, 0, 1, 2]
    30: "invalid hand (3)",  # e.g. [0, 0, 1, 2, 52]
    31: "triple",  # e.g. [0, 0, 1, 2, 3]
    40: "invalid hand (4)",  # e.g. [0, 1, 2, 3, 4]
    50: "invalid hand (5)",  # e.g. [1, 2, 3, 5, 52]
    51: "fullhouse",  # e.g. [1, 2, 3, 51, 52]
    52: "straight",  # e.g. [1, 5, 9, 13, 17]
    53: "bomb",  # e.g. [1, 49, 50, 51, 52]
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

    # not sure where to put support for being able to have more than 5
    # cards selected in a sort of queue? not sure this should even be
    # allowed since like if you have seven cards selected and then
    # remove one of the cards that was actually in the deck are the
    # queued cards added in order like honestly just don't like the idea
    # and will most likely just prevent it but don't know but prolly not

    def __init__(self, _cards=np.zeros(shape=5, dtype=np.uint8), _id=0,
                 _insertion_index=4) -> None:
        self._cards = _cards
        self._id = _id
        self._insertion_index = _insertion_index

    def __getitem__(self, key: Union[int, slice]) -> int:
        return self._cards[key]

    def __setitem__(self, key: Union[int, slice], card: int) -> None:
        self._cards[key] = card

    def __hash__(self) -> int:
        return hand_hash(self._cards)

    def __contains__(self, card: int) -> object:
        assert 1 <= card <= 52, "Bug: invalid card cannot be in hand."
        return card in self._cards

    def __repr__(self) -> str:
        return f"Hand({self._cards}; {self._id_desc})"

    def __eq__(self, other: object) -> bool:  # noqa: F821
        return (self._cards == other._cards and  # type: ignore
                self._id == other._id and  # type: ignore
                (self._insertion_index ==
                    other._insertion_index))  # type: ignore

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __lt__(self, other: Hand) -> bool:  # noqa: F821
        if not self._is_comparable(other):
            raise RuntimeError(
                f"{self._id_desc} cannot be played on {other._id_desc}.")
        if self._is_bomb and other._is_bomb:
            return self[1] < other[1]  # second card is always part of the quad
        elif self._is_bomb:
            return False
        elif other._is_bomb:
            return True
        elif self._is_single or self._is_double or self._is_straight:
            return self[4] < other[4]
        elif self._is_triple or self._is_fullhouse:
            return self[2] < other[2]
        else:
            raise AssertionError("Bug: unidentified hand.")

    def __gt__(self, other: Hand) -> bool:  # noqa: F821
        if not self._is_comparable(other):
            raise RuntimeError(
                f"{self._id_desc} cannot be played on {other._id_desc}.")
        if self._is_bomb and other._is_bomb:
            return self[1] > other[1]  # second card is always part of the quad
        elif self._is_bomb:
            return True
        elif other._is_bomb:
            return False
        elif self._is_single or self._is_double or self._is_straight:
            return self[4] > other[4]
        elif self._is_triple or self._is_fullhouse:
            return self[2] > other[2]
        else:
            raise AssertionError("Bug: unidentified hand.")

    def __le__(self, other: Hand) -> NoReturn:  # noqa: F821
        raise AssertionError('A <= call was made by a Hand.')

    def __ge__(self, other: Hand) -> NoReturn:  # noqa: F821
        raise AssertionError('A >= call was made by a Hand.')

    @property
    def _is_full(self) -> bool:
        return self._insertion_index == -1

    @property
    def _is_single(self) -> bool:
        return self._id == 11

    @property
    def _is_double(self) -> bool:
        return self._id == 21

    @property
    def _is_triple(self) -> bool:
        return self._id == 31

    @property
    def _is_fullhouse(self) -> bool:
        return self._id == 51

    @property
    def _is_straight(self) -> bool:
        return self._id == 52

    @property
    def _is_bomb(self) -> bool:
        return self._id == 53

    @property
    def _is_valid(self) -> bool:
        return self._id % 10 > 0

    @property
    def _number_of_cards(self) -> int:
        return 4 - self._insertion_index

    @property
    def _id_desc(self) -> str:
        return id_desc_dict[self._id]

    def _is_comparable(self, other: "Hand") -> bool:
        assert self._is_valid and other._is_valid, \
            "Bug: attempting to compare 1 or more invalid hands."
        if self._is_bomb or other._is_bomb:
            return True
        elif self._id != other._id:
            return False
        else:
            return True

    def _card_index(self, card: int) -> int:
        assert card in self, \
                "Bug: attempting to find index of card which is not in hand."
        return np.where(self._cards == card)[0][0]

    def _identify(self) -> None:
        h = hash(self)
        if h not in hand_table:
            self._id = self._number_of_cards * 10
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
        special sorting algorithm -- wow v algorithm
        best case big theta 1, worst case big theta 4
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

    def _remove(self, card) -> None:
        assert self._id != 0, "Bug: attempting to remove from an empty hand."
        ci = self._card_index(card)
        self[ci] = 0
        self._insertion_index += 1
        self._remove_sort(ci)
        self._identify()

    def _remove_sort(self, card_index: int) -> None:
        """
        special sorting algorithm -- wow v algorithm
        runs in big theta 1
        """
        ci = card_index
        ii = self._insertion_index
        self[ii + 1: ci + 1] = self[ii: ci]
        self[ii] = 0
