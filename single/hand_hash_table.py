import numpy as np
import deepdish as dd

from itertools import combinations as comb
from typing import Dict
from helpers import hand_hash, main


cards = np.arange(1, 53, dtype=np.uint8)
suits = cards.reshape(13, 4)


# hash table for identifying combos
hand_table: Dict[int, int] = {}


def _save_hand_table() -> None:
    dd.io.save("hand_table.h5", hand_table)


def _add_to_hand_table(hand, id) -> None:
    hand_table[hand_hash(hand)] = id


def _add_to_hand_table_iter(hands, id) -> None:
    for hand in hands:
        _add_to_hand_table(hand, id)


def _add_all() -> None:
    _add_singles()
    _add_doubles()
    _add_triples()
    _add_fullhouses()
    # _add_straight()
    _add_bombs()


def _add_singles() -> None:
    """
    adds all singles to the hand table
    """
    singles = np.zeros(shape=(52, 5), dtype=np.uint8)
    singles[:, 4] = range(1, 53)
    _add_to_hand_table_iter(singles, 11)


def _add_doubles() -> None:
    """
    adds all doubles to the hand table
    """
    doubles = np.zeros(shape=(6, 5), dtype=np.uint8)  # (4 C 2) = 6
    for suit in suits:
        doubles[:, 3:5] = list(comb(suit, 2))
        _add_to_hand_table_iter(doubles, 21)


def _add_triples() -> None:
    """
    adds all triples to the hand table
    """
    triples = np.zeros(shape=(4, 5), dtype=np.uint8)  # (4 C 3) = 4
    for suit in suits:
        triples[:, 2:5] = list(comb(suit, 3))
        _add_to_hand_table_iter(triples, 31)


def _add_fullhouses() -> None:
    """
    adds all fullhouses to the hand table
    """
    fullhouses = np.zeros(shape=(6, 5), dtype=np.uint8)
    for suit1, suit2 in comb(suits, 2):
        # double triples, e.g. [1, 2, 50, 51, 52]
        doubles = list(comb(suit1, 2))
        triples = comb(suit2, 3)
        fullhouses[:, 0:2] = doubles
        for triple in triples:
            fullhouses[:, 2:5] = triple  # numpy array broadcasting
            _add_to_hand_table_iter(fullhouses, 51)

        # triple doubles, e.g. [1, 2, 3, 51, 52]
        triples = comb(suit1, 3)
        doubles = list(comb(suit2, 2))
        fullhouses[:, 3:5] = doubles
        for triple in triples:
            fullhouses[:, 0:3] = triple  # numpy array broadcasting
            _add_to_hand_table_iter(fullhouses, 51)


def _add_bombs() -> None:
    """
    adds all bombs to the hand table
    """
    bombs = np.zeros(shape=(4, 5), dtype=np.uint8)
    for suit1, suit2 in comb(suits, 2):
        # single quads, e.g. [1, 49, 50, 51, 52]
        bombs[:, 0] = suit1
        bombs[:, 1:5] = suit2  # numpy array broadcasting
        _add_to_hand_table_iter(bombs, 53)

        # quad singles, e.g. [1, 2, 3, 4, 52]
        bombs[:, 0:4] = suit1  # numpy array broadcasting
        bombs[:, 4] = suit2
        _add_to_hand_table_iter(bombs, 53)



@main
def generate():
    _add_all()
    _save_hand_table()
