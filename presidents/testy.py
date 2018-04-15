from hand import Hand
from player import Player
from game import Game
import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
jsonpickle_numpy.register_handlers() 


a = Hand()
a._add(1)
a._add(5)
a._add(9)
a._add(13)
a._add(17)

b = jsonpickle.encode(a)
c = jsonpickle.decode(b)