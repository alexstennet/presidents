from itertools import combinations as it_comb, product as it_prod
import numpy as np
from scipy.special import comb
import deepdish as dd
from typing import Dict
from helpers import main

cards = np.arange(1, 53, dtype=np.uint8)
suits = cards.reshape(13, 4)

combo_dict: Dict[int, int] = {}


def save_combo_dict():
    dd.io.save("combo_dict.h5", combo_dict)


def populate():
    single()
    double()
    triple()
    fullhouse()
    # straight()
    # bomb()


def add_to_combo_dict(hand, combo):
    combo_dict[hash(hand.tostring())] = combo


def add_to_combo_dict_loop(hands, combo):
    for hand in hands:
        add_to_combo_dict(hand, combo)


def single():
    """
    adds all single hands to the combo dict
    """
    number_of_singles = 52
    singles = np.zeros(shape=(number_of_singles, 5), dtype=np.uint8)
    singles[:, 4] = np.arange(1, 53)
    add_to_combo_dict_loop(singles, 11)


def double():
    """
    adds all double hands to the combo dict
    """
    number_of_doubles = 13 * comb(4, 2, exact=True)
    doubles = np.zeros(shape=(number_of_doubles, 5), dtype=np.uint8)
    doubles_list = []
    for suit in suits:
        doubles_list.extend(it_comb(suit, 2))
    doubles_arr = np.array(doubles_list, dtype=np.uint8)
    doubles[:, 3:5] = doubles_arr
    add_to_combo_dict_loop(doubles, 21)


def triple():
    """
    adds all triple hands to the combo dict
    """
    number_of_triples = 13 * comb(4, 3, exact=True)
    triples = np.zeros(shape=(number_of_triples, 5), dtype=np.uint8)
    triples_list = []
    for suit in suits:
        triples_list.extend(it_comb(suit, 3))
    triples_arr = np.array(triples_list, dtype=np.uint8)
    triples[:, 2:5] = triples_arr
    add_to_combo_dict_loop(triples, 31)


def fullhouse():
    """
    adds all fullhouse hands to the combo dict
    """
    # combines double triples or triple doubles and adds to combo dict
    def combine_and_add(combos):
        hand = np.array(combos[0] + combos[1], dtype=np.uint8)
        add_to_combo_dict(hand, 41)

    for suit1, suit2 in it_comb(suits, 2):
        # double triples
        base_doubles = it_comb(suit1, 2)
        add_triples = it_comb(suit2, 3)
        dub_trip = it_prod(base_doubles, add_triples)
        for d_t in dub_trip:
            combine_and_add(d_t)

        # triple doubles
        base_triples = it_comb(suit1, 3)
        add_doubles = it_comb(suit2, 2)
        trip_dub = it_prod(base_triples, add_doubles)
        for t_d in trip_dub:
            combine_and_add(t_d)


@main
def generate():
    populate()
    save_combo_dict()
