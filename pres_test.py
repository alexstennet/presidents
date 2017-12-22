from sp_presidents import *

class test:
    a = [1,2,3]
    b = [4,5,6]
    # y = [sum(i,j) for i in a for j in b]



t = PresidentsTable()
p = t.game
p.debug = True
a = PresidentsPlayer('Adam')
b = PresidentsPlayer('Bobby')
c = PresidentsPlayer('Collin')
d = PresidentsPlayer('Dave')
for i in [a, b, c, d]:
    i.join_table(t)
a.cards = [
    Card('c','2',p),
]
b.cards = [
    Card('s','1',p),
]
c.cards = [
    Card('h','1',p),
]
d.cards = [
    Card('c','4',p),
]
t.start_game()
# hand c3 d3 h3 s3 h7
# hand cj dj hj sj cq
# hand dq hq sq


p = Presidents()
p0 = Presidents()
p1 = Presidents()
# h = PresidentsHand([Card('d', '3', p),
#                     Card('h', '3', p),
#                     Card('s', '3', p),
#                     Card('c', '4', p),
#                     Card('d', '4', p)])

j = PresidentsHand([Card('c', '1', p0),
                    Card('s', '1', p0),
                    Card('c', '7', p0),
                    Card('h', '7', p0),
                    Card('s', '7', p0)])

k = PresidentsHand([Card('c', '3', p0),
                    Card('d', '3', p0),
                    Card('d', '5', p0),
                    Card('h', '5', p0),
                    Card('s', '5', p0)])