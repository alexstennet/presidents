from sp_presidents import *

class test:
    a = [1,2,3]
    b = [4,5,6]
    # y = [sum(i,j) for i in a for j in b]



t = PresidentsTable()
p = t.game
a = PresidentsPlayer('Adam')
b = PresidentsPlayer('Bobby')
c = PresidentsPlayer('Collin')
d = PresidentsPlayer('Dave')
for i in [a, b, c, d]:
    i.join_table(t)
a.cards = [
    Card('c','3',p),
]
b.cards = [
    Card('c','7',p),
    Card('d','7',p),
    Card('h','7',p),
    Card('s','7',p),
    Card('c','8',p),
    Card('d','8',p),
    Card('h','8',p),
    Card('s','8',p),
    Card('c','9',p),
    Card('d','9',p),
    Card('h','9',p),
    Card('s','9',p),
    Card('d','6',p),
]
c.cards = [
    Card('c','j',p),
    Card('d','j',p),
    Card('h','j',p),
    Card('s','j',p),
    Card('c','2',p),
    Card('d','2',p),
    Card('h','2',p),
    Card('s','2',p),
    Card('c','q',p),
    Card('d','q',p),
    Card('h','q',p),
    Card('s','q',p),
    Card('h','6',p),
]
d.cards = [
    Card('c','k',p),
    Card('d','k',p),
    Card('h','k',p),
    Card('s','k',p),
    Card('c','a',p),
    Card('d','a',p),
    Card('h','a',p),
    Card('s','a',p),
    Card('c','1',p),
    Card('d','1',p),
    Card('h','1',p),
    Card('s','1',p),
    Card('s','6',p),
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