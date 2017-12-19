from helpers import main
from random import shuffle
from itertools import cycle, combinations

class Card:
    """
    class for cards and card comparisons
    """
    def __init__(self, suite, value):
        self.suite = suite
        self.value = value

    def same_suite(self, other):
        return self.suite == other.suite

    def same_value(self, other):
        return self.value == other.value

    def __repr__(self):
        return f'{self.suite}{self.value}'

class Deck:
    """
    Class for deck of cards, can be put on a table or removed
    from a table.
    """
    # a deck is a list of Card objects
    def __init__(self, cards=None):
        # if a custom deck of cards is not provided
        if not cards:
            # default deck of cards is modern standard deck of cards
            self.cards =\
                [Card(i, j) 
                    # 4 suites: clubs, diamonds, hearts, spades
                    # ordered from weakest to strongest
                    for i in ['c', 'd', 'h', 's']
                    # 13 values: 2-10 (zero-indexed) and jack, queen, king, ace
                    # ordered from weakest to strongest
                    for j in ['2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a', '1']
                ]
    
    def shuffle(self):
        shuffle(self.cards)
        print('Deck has been shuffled.')
    
    # generator that can yields each card in the deck
    def card_dealer(self):
        for card in self.cards:
            yield card

class Player:
    """
    Class for player, can view and play cards at whatever table
    spot they are at.
    """
    def __init__(self, name, spot=None, table=None):
        self.name = name
        self.spot = spot
        self.table = table

    # adds player to a table if there is an open spot
    # will add functionality for spectating in the future
    def join_table(self, table):
        open_spot = table.has_space()
        if open_spot:
            table.spots[open_spot] = self
            self.table = table
            self.spot = open_spot
        else:
            print('Table has no open spots.')

    def leave_table(self):
        if not self.table:
            print('Must be at a table to leave one.')
        else:
            self.table.spots[self.spot] = None
            self.spot = None
            self.table = None

    def view_cards(self):
        print(self.table.spots_cards[self.spot])

    def play(self, table, cards):
        return

    def __repr__(self):
        return f'{self.name} boi'

class Table:
    """
    Where players sit and play cards.
    """
    def __init__(self, game=None, deck=None):
        self.game = game
        self.deck = deck
        self.spots = {1: None, 2:None, 3:None, 4:None}
        self.spots_cards = {1: [], 2: [], 3: [], 4:[]}
        
    def add_game(self, game):
        self.game = game   

    def add_deck(self, deck):
        self.deck = deck

    # returns spot number of an open spot in the table
    # else returns False is there are no open spots
    def has_space(self):
        for spot in self.spots:
            if self.spots[spot] is None:
                return spot
        else:
            return False

    def shuffle_deck(self):
        self.deck.shuffle()

    def deal_cards(self):
        spot_cycler = cycle(self.spots.keys())
        # does not destruct the deck so the game can be replayed with the exact
        # same cards if desired
        dealer = self.deck.card_dealer()
        for card in dealer:
            next_spot = next(spot_cycler)
            self.spots_cards[next_spot].append(card)
        print('Cards have been dealt.')

    def start_game(self):
        self.game.play_game()

class Presidents:
    """
    Presidents card game class, contains all game logic.
    """
    
    def play_check():
        return

    def play_game():
        while True:
            return

class Hand:
    """
    Class for presidents hands, especially comparing hands
    """
    # starting hand that a hand with the 3 of clubs must be played on
    empty = ()

    def __init__(self, cards, valid=False):
        self.cards = cards

    def validate_and_label(self):
        if len(self) == 1:
            self.type = 'single'
        elif len(self) == 2:
            is_double(cards)
            self.valid = True
            self.type = 'double'
        elif len(self) == 3:
            is_triple(cards)
            self.type = 'triple'
        elif len(self) == 4:
            is_quad(cards)
            self.type = 'quad'
        elif len(self) == 5:
            if True:
                return
        
    def is_double(self):
        assert len(self) == 2, 'doubles consist of exactly 2 cards'
        # if both cards have the same value, the hand is a double
        return self.cards[0].same_value(self.cards[1])

    def is_triple(self):
        assert len(self) == 3, 'triples consist of exactly 3 cards'
        # if the first two cards form a double and last two cards form a
        # double, the hand is triple
        return self[0:2].is_double() and self[1:3].is_double()

    def is_quad(self):
        assert len(self) == 4, 'quads consist of exactly 4 cards'
        # if the first three cards form a triple and the last two cards form a
        # double, the hand can be a quad
        return self[0:3].is_triple() and self[2:4].is_double()

    def is_fullhouse(self):
        assert len(self) == 5, 'fullhouses consist of exactly 5 cards'
        # sort the cards by value and create a hand using them
        sorted_hand = Hand(sorted(self.cards, key=lambda x: x.value))
        # since the cards are sorted by value, then either the first, middle, or last
        # three cards will be a triple if a triple exists
        triple_exists = False
        for i in range(3):
            if sorted_hand[i:i+3].is_triple():
                triple_exists = True
                # break to store i as starting index for triple
                break
        # if no triple exists then the hand cannot possibly be a fullhouse
        if not triple_exists:
            return False
        else:
            # since we know the indeces where the triple was found, we need
            # only see if the cards at the remaining indeces can make a double
            remaining_indeces = set(range(5)) - set(range(i, i+3))
            i0, i1 = remaining_indeces
            # create a hand using the cards at the remaining indeces
            remaining_hand = sorted_hand[i0] + sorted_hand[i1]
            return remaining_hand.is_double()

    def is_straight(self):
        return

    def is_bomb(self):
        assert len(self) == 5, 'bombs consist of exactly 5 cards'
        # sort the cards by value and create a hand using them
        sorted_hand = Hand(sorted(self.cards, key=lambda x: x.value))
        # since the cards are sorted by value, then either the first or last
        # four cards being a quad will mean a bomb
        return sorted_hand[0:4].is_quad() or sorted_hand[1:5].is_quad()



            
        # check each card until a value is repeated, mark this as the fh_double, and
        # continue checking the rest of the cards

    def __getitem__(self, key):
        cards = self.cards[key]
        if not isinstance(cards, list):
            return Hand([cards])
        else:
            return Hand(cards)

    def __len__(self):
        return len(self.cards)

    def __add__(self, other):
        return Hand(self.cards + other.cards)

    def __repr__(self):
        return f'{[card for card in self.cards]}'
        
                
        
        

        self.cards = cards



    def can_play_on(self, curr_hand):
        if curr_hand is Hand.empty:
            return
   

    @property
    def type(self):
        if len(self.cards) == 1:
            return 'single'
        elif len(self.cards) == 2:
            return 'double'
        elif len(self.cards) == 3:
            return 'triple'




t = Table()
a = Player('a')
b = Player('b')
c = Player('c')
d = Player('d')
for i in [a, b, c, d]:
    i.join_table(t)
t.add_deck(Deck())
t.shuffle_deck()
t.deal_cards()

h = Hand([Card('c', '2'), Card('h', '2'), Card('s', '3'), Card('c', '2'), Card('s', '2')])
