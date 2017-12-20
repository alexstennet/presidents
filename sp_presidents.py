from helpers import main
from random import shuffle as rand_shuffle
from itertools import cycle

class Card:
    """
    class for cards and card comparisons
    """
    suite_dict = {'c': 'Clubs', 'd': 'Diamonds', 'h': 'Hearts', 's': 'Spades'}
    value_dict = {'1': 'Two', '2': 'Three', '3': 'Four', '4': 'Five', '5': 'Six',
                   '6': 'Seven', '7': 'Eight', '8': 'Nine', '9': 'Ten', 'j': 'Jack',
                   'q': 'Queen', 'k': 'King', 'a': 'Ace'}

    def __init__(self, suite, value, game=None):
        self.suite = suite
        self.value = value
        self.suite_value = self.suite + self.value
        self.game = game

    def same_suite(self, other):
        return self.suite == other.suite

    def same_value(self, other):
        return self.value == other.value

    

    def game_assert(self):
        assert self.game, 'This method requires a card tied to a game.'

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
        suite = self.suite_dict[self.suite]
        value = self.value_dict[self.value]
        return f'{value} of {suite}'

    def __str__(self):
        return self.suite_value


class Deck:
    """
    Class for deck of cards, can be put on a table or removed
    from a table.
    """
    # a deck is a list of Card objects
    def __init__(self, name='Standard', cards=[]):
        self.name = name
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
        else:
            # all cards in the deck must be Card objects
            for card in cards:
                assert isinstance(card, Card), 'all cards in a deck must be Card objects'
            self.cards = cards
    
    def shuffle(self):
        rand_shuffle(self.cards)
        print('Deck has been shuffled.')
    
    # generator that yields each card in the deck
    def card_dealer(self):
        for card in self.cards:
            yield card

    def __repr__(self):
        return f'{self.name} Deck'


class Player:
    """
    Class for player, can view and play cards at whatever table
    spot they are at.
    """
    def __init__(self, name, spot=None, table=None, game=None):
        self.name = name
        self.spot = spot
        self.table = table
        self.game = game

    # adds player to a table if there is an open spot
    # will add functionality for spectating in the future
    def join_table(self, table):
        open_spot = table.has_space()
        if open_spot:
            self.table = table
            self.table.spots[open_spot] = self  
            self.spot = open_spot
            if self.table.game:
                self.game = self.table.game
        else:
            print('Table has no open spots.')

    def leave_table(self):
        assert self.table, 'Must be at a table to leave one.'
        # leaves table but keeps the cards in that spot intact
        self.table.spots[self.spot] = None
        self.spot = None
        self.table = None
        self.game = None

    def create_hand(self, *cards):
        # *cards should be a comma separated list of suite_value strings of the
        # cards desired in the hand
        assert self.table, 'Must be at a table to create a hand'
        assert self.game, 'Must be playing a game to create a hand'
        suites_values = [card.suite_value for card in self.non_hands]
        hand_indeces = []
        # use suite_value's of each card to check if the player is creating a
        # hand using cards that they actually have
        for card in cards:
            assert card in suites_values, 'Card must be in your non-hands'
            hand_indeces.append(suites_values.index(card))
        # step through a reversed sorted version of the indeces so smaller
        # indeces remain intact while popping larger ones
        desired_cards = []
        for i in sorted(hand_indeces, reverse=True):
            desired_cards.append(self.non_hands.pop(i))
        # create a hand using the type of hand that the game provides
        desired_hand = self.game.hand(desired_cards)
        self.hands.append(desired_hand)

    def play_hand(self, hand_ind):
        assert self.table, 'Must be at a table to play cards.'
        assert len(self.hands) > hand_ind, 'There is not as many hands as you think.'
        if not self.hands[hand_ind].valid:
            self.hands[hand_ind].validate()
        

    def remove_from_hand(self, hand_ind, additional):
        return

    def add_to_hand(self, hand_ind, additional):
        return

    def unhand_hand(self, hand_ind):
        popped_hand = self.hands.pop(hand_ind)
        while popped_hand.cards:
            self.non_hands.append(popped_hand.cards.pop())
     
    def unhand_all_hands(self):
        for i in reversed(range(len(self.hands))):
            self.unhand_hand(i)

    def validate_hands(self):
        for hand in self.hands:
            hand.validate()

    @property
    def hands(self):
        assert self.table, 'Must be at a table to view hands'
        return self.table.hands[self.spot]

    @property
    def non_hands(self):
        assert self.table, 'Must be at a table to view non-hands'
        return self.table.cards[self.spot]

    @property
    def all(self):
        assert self.table, 'Must be at a table to view all cards'
        return self.table.hands[self.spot] + self.table.cards[self.spot]

    def __repr__(self):
        return f'player {self.name}'


class Table:
    """
    Where players sit and play card games.
    """
    def __init__(self, name='Flavorless', game=None, deck=None):
        self.name = name
        self.game = game
        # if the game comes with a deck, add the deck to the table
        if self.game.deck:
            self.add_deck(self.game.deck)
        else:
            self.deck = deck
        self.spots = {1: None, 2:None, 3:None, 4:None}
        # cards key corresponds to spots keys
        self.cards = {1: [], 2: [], 3: [], 4:[]}
        # hands key corresponds to spots keys
        self.hands = {1: [], 2: [], 3: [], 4:[]}
        self.played = []
        
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
            self.cards[next_spot].append(card)
        print('Cards have been dealt.')

    def start_game(self):
        self.game.play_game()

    def __repr__(self):
        return f'{self.name} Table'

class PresidentsTable(Table):
    """
    class for a table that is already set up for presidents
    """
    def __init__(self):
        Table.__init__(self, name='Presidents', game=Presidents())

class Hand:
    """
    simple Class for card hands
    """
    # a hand is a list of Card objects
    def __init__(self, cards=[]):
        for card in cards:
            assert isinstance(card, Card), 'all cards in a hand must be Card objects'
        self.cards = cards

    # allows indexing and slicing into Hands
    def __getitem__(self, key):
        cards = self.cards[key]
        if not isinstance(cards, list):
            return cards
        return self.__class__(cards)

    def __len__(self):
        return len(self.cards)

    # method to combine hands
    def __add__(self, other):
        return self.__class__(self.cards + other.cards)

    # method to check that a hand contains
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
            raise IndexError('Card is not in hand.')

    # def __iter__(self):
    #     return iter(self.cards)

    def __repr__(self):
        return f'Hand({[card for card in self.cards]})'
    
    
class PresidentsHand(Hand):
    """
    class for presidents hands
    """
    # starting hand that a hand with the 3 of clubs must be played on
    empty = []

    def __init__(self, cards=[]):
        Hand.__init__(self, cards)
        # check that all the cards in the hand are tied to presidents
        for card in self:
            assert isinstance(card.game, Presidents)
        # non-repeating pairwise comparison of cards in hand
        for i, card0 in enumerate(self.cards[:-1]):
            for card1 in self.cards[i+1:]:
                assert card0 != card1, 'All cards in a presidents hand must be unique.'
        self.valid = False

    # validate and label presidents hand
    def validate(self):
        if self.valid:
            pass  
        elif len(self) == 1:
            self.valid = True
            self.type = 'single'
        elif len(self) == 2:
            if self.is_double():
                self.valid = True
                self.type = 'double'
        elif len(self) == 3:
            if self.is_triple():
                self.valid = True
                self.type = 'triple'
        elif len(self) == 4:
            # whether or not we implement quads is still up for debate
            # if self.is_quad():
            #     self.valid = True
            #     self.type = 'quad'
            pass
        elif len(self) == 5:
            if self.is_bomb():
                self.valid = True
                self.type = 'bomb'
            elif self.is_fullhouse():
                self.valid = True
                self.type = 'fullhouse'
            elif self.is_straight():
                self.valid = True
                self.type = 'straight'
        self.validation_message()

    def is_double(self):
        assert len(self) == 2, 'Doubles consist of exactly 2 cards.'
        # if both cards have the same value, the hand is a double
        return self[0].same_value(self[1])

    def is_triple(self):
        assert len(self) == 3, 'Triples consist of exactly 3 cards.'
        # if the first two cards form a double and last two cards form a
        # double, the hand is triple
        return self[0:2].is_double() and self[1:3].is_double()

    # how quads are governed is still a hot topic of debate: in our regular play they
    # were always played with an extra card to make a bomb that beats everything except
    # higher bombs but how exactly should quads work if we don't really have a sample of 
    # people even using them because of the exsitence of bombs?    
    def is_quad(self):
        assert len(self) == 4, 'Quads consist of exactly 4 cards.'
        # if the first three cards form a triple and the last two cards form a
        # double, the hand can be a quad
        return self[0:3].is_triple() and self[2:4].is_double()

    def is_fullhouse(self):
        assert len(self) == 5, 'Fullhouses consist of exactly 5 cards.'
        # sort the cards by value and create a hand using them
        sorted_hand = PresidentsHand(sorted(self))
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
            remaining_hand = PresidentsHand([sorted_hand[i0], sorted_hand[i1]])
            return remaining_hand.is_double()

    def is_straight(self):
        assert len(self) == 5, 'straights consist of exactly 5 cards'
        # we won't be using any Hand methods to compare cards so let's simply
        # sort them without turning them into a hand
        sorted_cards = sorted(self)
        # once the cards are lined up in order, we want to pair subsequent cards
        for card0, card1 in zip(sorted_cards[:-1], sorted_cards[1:]):
            # determine the value's position in the Presidents value order 
            pos0 = Presidents.value_order.index(card0.value)
            pos1 = Presidents.value_order.index(card1.value)
            # subsequent cards must have value 1 greater than the last to form
            # a straight
            if pos0 + 1 != pos1:
                return False
        return True
        
    def is_bomb(self):
        assert len(self) == 5, 'bombs consist of exactly 5 cards'
        # sort the cards by value and create a hand using them
        sorted_hand = PresidentsHand(sorted(self))
        # since the cards are sorted by value, then either the first or last
        # four cards being a quad will mean a bomb
        return sorted_hand[0:4].is_quad() or sorted_hand[1:5].is_quad()

    def validation_message(self):
        if self.valid:
            print(f'{self} is a valid {self.type} hand.')
        else:
            print(f'{self} is not a valid hand.')
    
class Presidents:
    """
    Presidents card game class, contains idk.
    """    
    suite_order = ['c', 'd', 'h', 's']
    value_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a', '1']
    hand = PresidentsHand

    def __init__(self):
        # president's card deck, with cards ordered from weakest to strongest
        self.deck = Deck('Presidents',
            [Card(j, i, self) 
                # 4 suites: clubs, diamonds, hearts, spades
                # ordered from weakest to strongest
                for i in ['2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a', '1']
                # 13 values: 2-10 (zero-indexed) and jack, queen, king, ace
                # ordered from weakest to strongest
                for j in ['c', 'd', 'h', 's']])

    @property
    def order(self):
        return self.deck.cards
    
    def __repr__(self):
        return 'Presidents Game Instance'












t = PresidentsTable()
a = Player('a')
b = Player('b')
c = Player('c')
d = Player('d')
for i in [a, b, c, d]:
    i.join_table(t)
t.shuffle_deck()
t.deal_cards()

p = Presidents()
h = PresidentsHand([Card('c', 'k', p),
                    Card('d', '9', p),
                    Card('h', '8', p),
                    Card('s', '4', p),
                    Card('c', '5', p)])