from helpers import main
from random import shuffle as rand_shuffle
from itertools import cycle, combinations

class Card:
    """
    class for cards and card comparisons
    """
    def __init__(self, suite, value, game=None):
        self.suite = suite
        self.value = value
        self.game = game

    def same_suite(self, other):
        return self.suite == other.suite

    def same_value(self, other):
        return self.value == other.value

    def __lt__(self, other):
        self.game_assert()
        # convert the game's order to a (invalid) Hand so we can check if
        # the card is in the list of game cards; this method follows for
        # the rest of the comparisons 
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) < game_cards_hand.index(other)

    def __le__(self, other):
        self.game_assert()
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) <= game_cards_hand.index(other)

    def __eq__(self, other):
        self.game_assert()
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) == game_cards_hand.index(other)

    def __ne__(self, other):
        self.game_assert()
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) != game_cards_hand.index(other)

    def __ge__(self, other):
        self.game_assert()
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) >= game_cards_hand.index(other)

    def __gt__(self, other):
        self.game_assert()
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) > game_cards_hand.index(other)

    def __repr__(self):
        return f'{self.suite}{self.value}'

    def game_assert():
        assert self.game, 'This method requires a card tied to a game.'

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
                    for j in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a']
                ]
    
    def shuffle(self):
        rand_shuffle(self.cards)
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
    Presidents card game class, contains idk.
    """
    # president's card deck, with cards ordered from weakest to strongest
    ordered_deck =\
        [Card(j, i) 
            # 4 suites: clubs, diamonds, hearts, spades
            # ordered from weakest to strongest
            for i in ['2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a', '1']
            # 13 values: 2-10 (zero-indexed) and jack, queen, king, ace
            # ordered from weakest to strongest
            for j in ['c', 'd', 'h', 's']
        ]

    
        


    @property
    def order(self):
        return self.ordered_deck

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
        self.valid = valid

    def validate_and_label(self):
        if len(self) == 1:
            self.valid = True
            self.type = 'single'
            self.validation_message()
        elif len(self) == 2:
            if self.is_double():
                self.valid = True
                self.type = 'double'
            self.validation_message()
        elif len(self) == 3:
            if self.is_triple():
                self.valid = True
                self.type = 'triple'
            self.validation_message()
        elif len(self) == 4:
            if self.is_quad():
                self.valid = True
                self.type = 'quad'
            self.validation_message()
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

    # how quads are governed is still a hot topic of debate: in our regular play they
    # were always played with an extra card to make a bomb that beats everything except
    # higher bombs but how exactly should quads work if we don't really have a sample of 
    # people even using them because of the exsitence of bombs?    
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
        assert len(self) == 5, 'straights consist of exactly 5 cards'
        # we won't be using any Hand methods to compare cards so let's simply
        # sort them without turning them into a hand
        sorted_cards = sorted(self.cards, key=lambda x: x.value)


    def is_bomb(self):
        assert len(self) == 5, 'bombs consist of exactly 5 cards'
        # sort the cards by value and create a hand using them
        sorted_hand = Hand(sorted(self.cards, key=lambda x: x.value))
        # since the cards are sorted by value, then either the first or last
        # four cards being a quad will mean a bomb
        return sorted_hand[0:4].is_quad() or sorted_hand[1:5].is_quad()


    
    def validation_message(self):
        if self.valid:
            print(f'This is a valid {self.type} hand.')
        else:
            print('This is not a valid hand.')

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

    def __contains__(self, other):
        for card in self.cards:
            if card.same_suite(other) and card.same_value(other):
                return True
        else:
            return False
    
    def index(self, other):
        if other in self:
            for i, card in enumerate(self.cards):
                if card.same_suite(other) and card.same_value(other):
                    return i
        else:
            raise IndexError('card is not in hand')

    def __repr__(self):
        return f'{[card for card in self.cards]}'
    



    def can_play_on(self, curr_hand):
        if curr_hand is Hand.empty:
            return




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

h = Hand([Card('c', '1'), Card('h', '1'), Card('s', '2')])
p = Presidents()
c2 = Card('c', '1', p)
c22 = Card('c', '3', p)