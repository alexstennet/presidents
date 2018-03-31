import itertools
import numpy as np
from numba import jit
from numba import void, uint8
from scipy.special import comb
import deepdish as dd
from helpers import main

cards = np.arange(1, 53, dtype=np.uint8)
suits = cards.reshape(13, 4)

combo_dict = {}


@jit(void(uint8[:, :], uint8), nopython=True, nogil=True, parallel=True)
def add_to_combo_dict(hands, combo):
    for hand in hands:
        combo_dict[hash(hand.tostring())] = np.uint8(combo) 


@jit
def single():
    """
    adds all single hands to the combo dict
    """
    number_of_singles = 52
    singles = np.zeros(shape=(number_of_singles, 5), dtype=np.uint8)
    singles[:, 4] = np.arange(1, 53)
    add_to_combo_dict(singles, 1)


@jit
def double():
    """
    adds all double hands to the combo dict
    """
    number_of_doubles = 13 * comb(4, 2, exact=True)
    doubles = np.zeros(shape=(number_of_doubles, 5), dtype=np.uint8)
    doubles_list = []
    for suit in suits:
        doubles_list.extend(itertools.combinations(suit, 2))
    doubles_arr = np.array(doubles_list, dtype=np.uint8)
    doubles[:, 3:5] = doubles_arr
    add_to_combo_dict(doubles, 2)


@jit
def triple():
    """
    adds all triple hands to the combo dict
    """
    number_of_triples = 13 * comb(4, 3, exact=True)
    triples = np.zeros(shape=(number_of_triples, 5), dtype=np.uint8)
    triples_list = []
    for suit in suits:
        triples_list.extend(itertools.combinations(suit, 3))
    triples_arr = np.array(triples_list, dtype=np.uint8)
    triples[:, 2:5] = triples_arr
    add_to_combo_dict(triples, 3)


@main
@jit
def populate_and_save_combo_dict():
    single()
    double()
    triple()
    dd.io.save("combo_dict.h5", combo_dict)
