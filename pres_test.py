from sp_presidents import *

# class test:
#     a = [1,2,3]
#     b = [4,5,6]
#     # y = [sum(i,j) for i in a for j in b]



# t = PresidentsTable()
# p = t.game
# p.debug = True
# a = PresidentsPlayer('Adam')
# b = PresidentsPlayer('Bobby')
# c = PresidentsPlayer('Collin')
# d = PresidentsPlayer('Dave')
# for i in [a, b, c, d]:
#     i.join_table(t)
# a.cards = [
#     Card('c','2',p),
# ]
# b.cards = [
#     Card('s','1',p),
# ]
# c.cards = [
#     Card('h','1',p),
# ]
# d.cards = [
#     Card('c','4',p),
# ]
# t.start_game()
# hand c3 d3 h3 s3 h7
# hand cj dj hj sj cq
# hand dq hq sq


# p0 = Presidents()
# p1 = Presidents()
# card1 = PresidentsCard('s', '1')
# card2 = PresidentsCard('d', '1')

# # h = PresidentsHand([Card('d', '3', p),
# #                     Card('h', '3', p),
# #                     Card('s', '3', p),
# #                     Card('c', '4', p),
# #                     Card('d', '4', p)])

# j = PresidentsHand([PresidentsCard('c', '1'),
#                     PresidentsCard('s', '1'),
#                     PresidentsCard('c', '7'),
#                     PresidentsCard('h', '7'),
#                     PresidentsCard('s', '7')])

# k = PresidentsHand([PresidentsCard('c', '3'),
#                     PresidentsCard('d', '3'),
#                     PresidentsCard('d', '5'),
#                     PresidentsCard('h', '5'),
#                     PresidentsCard('s', '5')])

t = PresidentsTable()
s = PresidentsSpot(table=t)
p = PresidentsPlayer('Player')
s.add_player(p)
s.cards = [PresidentsCard('c', '3'),
           PresidentsCard('d', '3'),
           PresidentsCard('d', '5'),
           PresidentsCard('h', '5'),
           PresidentsCard('s', '5')]
p.create_hand('c4', 'd4', 'd6', 'h6', 's6')

# h = Hand([PresidentsCard('c', '3'),
#            PresidentsCard('d', '3'),
#            PresidentsCard('d', '5'),
#            PresidentsCard('h', '5'),
#            PresidentsCard('s', '5')])