import random
from itertools import cycle

class Card:
    """A general class for cards in a standard 52-card deck.

    These cards need not be tied to any particular card game but some of
    their methods depend on the game they are being used for, namely,
    comparing cards with each other.
    """
    suite_dict = {'c': 'Clubs', 'd': 'Diamonds', 'h': 'Hearts', 's': 'Spades'}
    # Note that the card values are zero-indexed to avoid having to
    # store cards with value 10 with an additional character. Although
    # this slightly confusing convention (you'll get used to it) is
    # present in the backend and database, all implementations of UI
    # will present card values as one would expect.
    value_dict = {'1': '2', '2': '3', '3': '4', '4': '5', '5': '6', '6': '7',
                  '7': '8', '8': '9', '9': '10', 'j': 'Jack', 'q': 'Queen',
                  'k': 'King', 'a': 'Ace'}
    BEDB_to_UI_dict = {'1': '2', '2': '3', '3': '4', '4': '5', '5': '6',
                       '6': '7', '7': '8', '8': '9', '9': '10', 'a': 'a',
                       'j': 'j', 'q': 'q', 'k': 'k'}
    UI_to_BEDB_dict = {'2': '1', '3': '2', '4': '3', '5': '4', '6': '5',
                       '7': '6', '8': '7', '9': '8', '10': '9', 'j': 'j',
                       'q': 'q', 'k': 'k', 'a': 'a'}

    def __init__(self, suite, value):
        if not isinstance(suite, str):
            raise TypeError(
                "Suites are the single letter strings: 'c', 'd', 'h', 's'.")
        if not isinstance(value, str):
            raise TypeError(
                'Values must be given as strings, even for cards with numeric '
                'values.')
        if suite not in Card.suite_dict:
            raise ValueError(
                "The only suites in the standard 52-card deck are: 'c', 'd', "
                "'h', 's'.")
        if value not in Card.value_dict:
            raise ValueError(
                'All values are zero-indexed, e.g. use 9 for 10, etc.')
        self.suite = suite
        self.value = value
        self.suite_value = self.suite + self.value

    def same_suite(self, other):
        return self.suite == other.suite

    def same_value(self, other):
        return self.value == other.value

    def same_card(self, other):
        return self.same_suite(other) and self.same_value(other)

    @property
    def UI_suite_value(self):
        suite, value = self.suite, self.value
        return suite + Card.BEDB_to_UI_dict[value]

    # Replace these methods if this basic equality definition must be
    # expanded or simply does not apply.
    def __eq__(self, other):
        return self.same_card(other)

    def __ne__(self, other):
        return not self == other

    # All other card comparison methods must be provided by the subclass
    # of the Card class corresponding to the game being played as rules
    # dictating the value of cards varies per card game.
    def __lt__(self, other):
        raise NotImplementedError(
            'The < method must be provided by the subclass of the Card class '
            'corresponding to the game being played.')

    def __le__(self, other):
        raise NotImplementedError(
            'The <= method must be provided by the subclass of the Card class '
            'corresponding to the game being played.')

    def __ge__(self, other):
        raise NotImplementedError(
            'The > method must be provided by the subclass of the Card class '
            'corresponding to the game being played.')

    def __gt__(self, other):
        raise NotImplementedError(
            'The >= method must be provided by the subclass of the Card class '
            'corresponding to the game being played.')

    def __repr__(self):
        suite = self.suite_dict[self.suite]
        value = self.value_dict[self.value]
        return f'{value} of {suite}'

    # Note the result of printing or str-ing a card returns its backend/
    # database representation (i.e. zero-indexed values for 2-10)
    def __str__(self):
        return self.suite_value


class Deck:
    """
    A simple class for decks of cards.
    """
    # A deck is a list of Card objects
    def __init__(self, cards=[], name='Standard'):
        self.name = name
        # If a custom deck of cards is not provided:
        if not cards:
            # Default deck of cards is the standard 52-card deck.
            self.cards =\
                [Card(i, j)
                 # 4 suites: clubs, diamonds, hearts, spades
                 for i in ['c', 'd', 'h', 's']
                 # 13 values: 2-10 (zero-indexed) and jack, queen, king, ace
                 for j in ['1', '2', '3', '4', '5', '6',
                           '7', '8', '9', 'j', 'q', 'k', 'a']]
        else:
            for card in cards:
                if not isinstance(card, Card):
                    raise TypeError(
                        'All cards in a deck must be Card objects.')
            self.cards = cards

    def shuffle(self):
        random.shuffle(self.cards)
        print('Deck has been shuffled.')

    # Generator that yields each card in the deck.
    def card_dealer(self):
        for card in self.cards:
            yield card

    def __repr__(self):
        return f'{self.name} Deck'

class Player:
    """
    A general class for card game players.
    """
    def __init__(self, name):
        self.name = name
        self.spot = None

    def enter_spot(self, spot):
        # In the future, this should send a request to the table to add the
        # player if there is space for them.
        if not isinstance(spot, Spot):
            raise TypeError(
                'Players can only enter instances of the Spot class.')
        spot.add_player(self)

    def leave_spot(self):
        # In the future, this should send a request to the table to remove
        # the player from the table (at the next most appropriate time.)
        if not self.spot:
            raise RuntimeError(
                'Player cannot leave a spot if they are not in one.')
        self.spot.remove_player()

    def create_hand(self):
        raise NotImplementedError(
            'The create_hand method must be provided by the subclass of the '
            'Player class corresponding to the game being played.')

    def play_hand(self):
        raise NotImplementedError(
            'The create_hand method must be provided by the subclass of the '
            'Player class corresponding to the game being played.')

    @property
    def table(self):
        if not self.spot:
            raise RuntimeError('Players must be in a spot to access table.')
        return self.spot.table

    @property
    def hands(self):
        if not self.spot:
            raise RuntimeError('Players must be in a spot to access hands.')
        return self.spot.hands

    @property
    def cards(self):
        if not self.spot:
            raise RuntimeError('Players must be in a spot to access cards.')
        return self.spot.cards

    @property
    def all(self):
        if not self.spot:
            raise RuntimeError(
                'Players must be in a spot to access hands and cards.')
        return self.spot.all

    def __repr__(self):
        return self.name

class Spot:
    """A class for spots at a table.
    """
    def __init__(self, table):
        if not isinstance(table, Table):
            raise TypeError('Table must be a Table object.')
        self.table = table
        self.player = None
        self.cards = []
        self.hands = []

    @property
    def all(self):
        return self.hands + self.cards

    def add_player(self, player):
        if self.player:
            raise RuntimeError(
                'Player must be removed from spot before another is added.')
        if not isinstance(player, Player):
            raise TypeError(
                'Only instances of the Player class can be added to a spot.')
        self.player = player
        player.spot = self

    def remove_player(self):
        if not self.player:
            raise RuntimeError(
                'Player cannot be removed if the spot does not have one.')
        self.player.spot = None
        self.player = None

    @property
    def empty_handed(self):
        return self.all == []

    def clear_cards(self):
        self.cards = []

    def clear_hands(self):
        self.hands = []

    def __repr__(self):
        return f'Spot(player:{self.player})'


class Table:
    """
    Where players sit and play card games; holds instances of the Spot
    class.
    """
    def __init__(self, name='Flavorless', num_spots=4, spot=Spot):
        self.spots = []
        for _ in range(num_spots):
            self.add_spot(spot(table=self))
        self.name = name
        self.game = None
        self.played = []

    def add_spot(self, spot):
        if not isinstance(spot, Spot):
            raise TypeError('Spot must be a Spot object.')
        self.spots.append(spot)

    def add_game(self, game):
        if not isinstance(game, CardGame):
            raise TypeError(
                'Only instances of the CardGame class can be added as a game.')
        self.game = game
        self.game.table = self

    @property
    def deck(self):
        return self.game.deck

    def add_player(self, player):
        if not isinstance(player, Player):
            raise TypeError(
                "Only instances of the Player class can be added to a "
                "table('s spot)")
        spot = self.open_spot
        if spot:
            spot.add_player(player)
        else:
            raise RuntimeError('Table has no open spots.')

    def remove_player(self, player):
        if not player in [spot.player for spot in self.spots]:
            raise RuntimeError(
                'Player is not in any of the spots at the table.')

    # Returns a spot if there is an open one and False otherwise.
    @property
    def open_spot(self):
        for spot in self.spots:
            if spot.player is None:
                return spot
        else:
            return False

    def shuffle_deck(self):
        self.deck.shuffle()

    def spot_cycler(self):
        for spot in cycle(self.spots):
            yield spot

    def deal_cards(self):
        spot_cycler = self.spot_cycler()
        dealer = self.deck.card_dealer()
        for card in dealer:
            spot = next(spot_cycler)
            spot.cards.append(card)
        print('Cards have been dealt.')

    def start_game(self):
        self.game.play_game()

    def clear_played(self):
        self.played = []

    def clear_cards(self):
        for spot in self.spots:
            spot.clear_cards()
            spot.clear_hands()

    @property
    def last(self):
        return self.played[-1]

    @property
    def players(self):
        return [spot.player for spot in self.spots]

    def __repr__(self):
        return f'{self.name} Table'


class Hand:
    """
    Simple class for card hands.
    """
    # a hand is a list of Card objects
    def __init__(self, cards):
        for card in cards:
            if not isinstance(card, Card):
                raise TypeError('All cards in a hand must be Card objects.')
        self.cards = cards

    # Allows indexing and slicing into Hands
    def __getitem__(self, key):
        cards = self.cards[key]
        # Returns individual card if not slicing
        if isinstance(cards, Card):
            return cards
        elif isinstance(cards, list):
            if cards == []:
                return []
            return self.__class__(cards)
        else:
            raise AssertionError(
                f'Impossible type ({type(cards)}) returned when'
                 'indexing/slicing.')

    def __len__(self):
        return len(self.cards)

    def __contains__(self, other):
        return other in self.cards

    def index(self, other):
        return self.cards.index(other)

    def __add__(self, other):
        return self.__class__(self.cards + other.cards)

    def __repr__(self):
        return f'Hand({[card for card in self.cards]})'

    # subclasses of the Hand class must provide their own hand
    # comparison criteria; the alternative to this was requiring
    # subclasses of the hand class to explicitly enumerate all card
    # combinations/permutations in order for the Hand class to then
    # interpret, and even then, I'm not sure how it would handle
    # comparison rules, e.g. comparing hands of different sizes

    def __lt__(self, other):
        raise NotImplementedError(
            'The < method must be provided by the subclass of the Hand class '
            'corresponding to the game being played.')

    def __le__(self, other):
        raise NotImplementedError(
            'The <= method must be provided by the subclass of the Hand class '
            'corresponding to the game being played.')

    def __eq__(self, other):
        raise NotImplementedError(
            'The == method must be provided by the subclass of the Hand class '
            'corresponding to the game being played.')

    def __ne__(self, other):
        raise NotImplementedError(
            'The != method must be provided by the subclass of the Hand class'
            'corresponding to the game being played.')

    def __ge__(self, other):
        raise NotImplementedError(
            'The >= method must be provided by the subclass of the Hand class '
            'corresponding to the game being played.')

    def __gt__(self, other):
        raise NotImplementedError(
            'The > method must be provided by the subclass of the Hand class '
            'corresponding to the game being played.')


class CardGame:
    """
    generic card game class
    """
    def __repr__(self):
        'A card game'
