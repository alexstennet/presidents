from hand import Hand
from hand_list import HandList
from json import loads, dumps


a = Hand()
a.add(1)
a.add(5)
a.add(9)
a.add(13)
a.add(17)

c = Hand([2,49,50,51,52])

b = HandList()

b.add(a)
b.add(c)