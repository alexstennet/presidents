import numpy as np

from hand import Hand
from hand_list import HandList
from card_hand_chamber import CardHandChamber

a = np.arange(1, 14)

b = CardHandChamber(a)

c = Hand([0, 0, 0, 1, 2])
d = Hand([0, 0, 0, 2, 3])

b.add_hand(c)
b.add_hand(d)
