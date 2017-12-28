import random
import readline
from itertools import cycle, combinations
from ansimarkup import parse
from helpers import main


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
    UI_to_BEDB_dict = {'2': '1', '3': '2', '4': '3', '5': '4', '6': '5',
                       '7': '6', '8': '7', '9': '8', '10': '9', 'j': 'j',
                       'q': 'q', 'k': 'k', 'a': 'a'}
    BEDB_to_UI_dict = {j: i for i, j in UI_to_BEDB_dict.items()}

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


class PresidentsCard(Card):
    """A class for presidents cards, mainly dictating card comparisons.
    """
    # In order to compare a card with another, we need only compare each
    # card's position in the President's card order. The same follows
    # for the greater than method.
    def __lt__(self, other):
        return Presidents.order.index(self) < Presidents.order.index(other)

    def __gt__(self, other):
        return Presidents.order.index(self) > Presidents.order.index(other)

    # Calls to <= and >= should never be made as they don't make sense
    # in the context of presidents
    def __le__(self, other):
        raise AssertionError('A <= call was made by a PresidentsCard.')

    def __ge__(self, other):
        raise AssertionError('A >= call was made by a PresidentsCard.')


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
                    for j in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'j',
                              'q', 'k', 'a']]
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


class PresidentsPlayer(Player):
    """
    class for presidents players.
    """
    is_human = True
    
    def __init__(self, name):
        Player.__init__(self, name)
        self.func_dict = \
        {   
        'view': (self.view,
            "'view cards': show cards\n            'view hands': show hands\n            'view all': show cards and hands\n            'view last': show what you have to beat, if anything"),
        'hand': (self.create_hand,
            "use shorthand versions of card names separated by spaces to create a hand,\n            e.g. 'hand s2 h2 d2 c2 sa' creates a 2 bomb with an Ace of Spades"),
        'unhand': (self.unhand_hand,
            "remove the hand at index i\n            i.e. 'unhand i' removes the i-th hand from the list of hands"),
        'play': (self.play_hand, 
            "play the hand at index i\n            i.e. 'play i' plays the i-th hand in hands\n            view hands and corresponding index with 'view hands'\n            alternatively, play singles without creating a hand by using shorthand card names\n            e.g. 'play s2' plays the 2 of Spades"),
        'pass': (self.pass_turn,
            'pass on the current hand being played on'),
        'help': (self.help,
            'list the command options and short descriptions of each'),
        }
        
    def create_hand(self, *cards):
        # *cards should be comma separated UI suite_value strings (i.e
        # the ones that are NOT zero-indexed) of the cards desired in
        # the hand.
        if not self.spot:
            raise RuntimeError('Player must be in a spot to create a hand.')
        # Convert the UI suite_value strings to backend/database
        # suite_value strings; this will KeyError if the the card value 
        # given is not valid.
        try:
            # Could not use list comprehension because card assignment
            # is lost and exception requires card to be assigned.
            temp_cards = []
            for card in cards:
                temp_cards.append(card[0]+Card.UI_to_BEDB_dict[card[1:]])
        except:
            raise ValueError(
                f"{card[1:]} is not a valid card value; they are '2'-'10', 'j'"
                 ", 'q', 'k', 'a'.")
        else:
            cards = temp_cards
        # Convert suite_value strings to Card objects; this will
        # ValueError if if the card suite given is not valid; error
        # message is included.
        cards_objs = []
        for suite, value in cards:
            cards_objs.append(PresidentsCard(suite, value))
        # Check that the player has the cards they want to make a hand 
        # using.
        desired_cards = []
        for card in cards_objs:
            if card not in self.cards:
                raise RuntimeError(
                    f'You do not have the {card}')
            else:
                desired_cards.append(card)
        desired_hand = PresidentsHand(desired_cards)
        if len(desired_hand) == 1 or not self.is_human:
            # No need to announce that a single is a valid hand.
            desired_hand.validate(print_message=False)
        else:
            desired_hand.validate(print_message=True)
        # Only valid hands should be added to the player('s spot)'s
        # hands
        if desired_hand.valid:
            self.hands.append(desired_hand)
        
    def play_hand(self, hand_ind):
        if not self.spot:
            raise RuntimeError('Player must be in a spot to play a hand.')
        # Allow hands to be single card, UI suite_value strings and do 
        # the hand building automatically
        if isinstance(hand_ind, str):
            # Check if hand_ind is a string with a valid suite for the
            # first letter
            if hand_ind[0] in Presidents.suite_order:
                self.create_hand(hand_ind)
                # After creating the single card hand, try to play it.
                try:
                    self.play_hand(-1)
                # If it can't be played, unhand the created hand.
                except:
                    self.unhand_hand(-1)
                    raise
                return
        hand_ind = self.hand_ind_check(hand_ind)
        hand_to_play = self.hands[hand_ind]
        # if the hand wanting to played is not valid, attempt to
        # validate it
        assert hand_to_play.valid, \
            'Invalid hands should not be able to get to this point.'
        last_played = self.table.last_played
        passes = self.table.passes_on_top
        if self.has_3_of_clubs:
            if not Card('c','2') in hand_to_play:
                raise RuntimeError(
                    'The starting hand must contain the 3 of Clubs!')
            self.force_play_hand(hand_ind, hand_to_play)
        else:
            if self.can_play_anyhand:
                self.force_play_hand(hand_ind, hand_to_play)
            else:
                if hand_to_play < last_played:
                    raise RuntimeError(
                        f'{hand_to_play.cards} cannot beat '
                         '{last_played.cards}.')
                self.force_play_hand(hand_ind, hand_to_play)

    def force_play_hand(self, hand_ind, hand_to_play=None):
        hand_ind = self.hand_ind_check(hand_ind)
        if not hand_to_play:
            hand_to_play = self.hands[hand_ind]
        self.spot.remove_intersecting(hand_to_play)
        self.table.play(hand_to_play)

    def pass_turn(self):
        if not self.spot:
            raise RuntimeError('Player must be in a spot to pass.')
        if self.has_3_of_clubs:
            raise RuntimeError('Cannot pass when you have the 3 of Clubs!')
        if self.can_play_anyhand:
            print('No one beat the last hand; play anyhand you want!')
        else:
            self.table.play(PresidentsPass())

    @property
    def has_3_of_clubs(self):
        return self.spot.has_3_of_clubs

    @property
    def can_play_anyhand(self):
        return self.spot.can_play_anyhand

    def unhand_hand(self, hand_ind):
        if not self.spot:
            raise RuntimeError('Player must be in a spot to unhand a hand.')
        if hand_ind == 'all':
            self.unhand_all_hands()
            return
        hand_ind = self.hand_ind_check(hand_ind)
        self.hands.pop(hand_ind)
        
    def unhand_all_hands(self):
        if not self.spot:
            raise RuntimeError('Player must be in a spot to unhand all hands.')
        self.spot.clear_hands()

    def hand_ind_check(self, hand_ind):
        try:
            hand_ind = int(hand_ind)
        except:
            raise ValueError('Desired hand index must be an integer.')
        if len(self.hands) <= hand_ind:
            raise ValueError('There are not as many hands as you think.')
        return hand_ind
    
    @property
    def empty_handed(self):
        return self.spot.empty_handed
    
    def view(self, which):
        if which == 'all':
            self.view('cards')
            self.view('hands')
        elif which == 'hands':
            for i, hand in enumerate(self.hands):
                print(f'{i}: {hand.cards}')
        elif which == 'cards':
            print(sorted(self.cards))
        elif which == 'last':
            if self.has_3_of_clubs:
                print('You must play a something with the 3 of Clubs!')
            elif self.can_play_anyhand:
                print(f'You can play any hand you want!')
            else:
                print(f'What you have to beat: {self.table.last_played.cards}')
        else:
            print(
                f"{which} is not a valid argument for view. Enter 'help' to "
                 "see your options!")

    def help(self):
        for shortcut, info in self.func_dict.items():
            print(f'{shortcut.ljust(10)}: {info[1].rjust(10)}')

    def func_lookup(self, shortcut):
        # returns None if the function is not in the player function
        # dictionary
        func = self.func_dict.get(shortcut)
        if func:
            return func[0]


class AIPresidentsPlayer(PresidentsPlayer):
    """Class for a super basic AI presidents player.
    
    This AI simply checks its cards for anything that can beat the last
    hand and plays it no matter what.
    """
    is_human = False
    
    def play_or_pass(self):
        # If the AI has the 3 of Clubs, play it
        if self.has_3_of_clubs:
            self.play_hand('c3')
        # If the AI can play anyhand, simple play the lowest single
        if self.can_play_anyhand:
            min_card = min(self.cards)
            self.play_hand(min_card.UI_suite_value)
            return
        hand_to_beat = self.table.last_played
        beater = self.hand_if_can_beat(hand_to_beat)
        if beater:
            self.create_hand(*beater)
            self.play_hand(-1)
        else:
            self.pass_turn()

    def hand_if_can_beat(self, hand_to_beat):
        type = hand_to_beat.type
        if type == 'single':
            return self.higher_single(hand_to_beat)
        elif type == 'double':
            return self.higher_double(hand_to_beat)
        elif type == 'triple':
            return self.higher_triple(hand_to_beat)
        elif type == 'fullhouse':
            return self.higher_fullhouse(hand_to_beat)
        elif type == 'straight':
            return self.higher_straight(hand_to_beat)
        elif type == 'bomb':
            return self.higher_bomb(hand_to_beat)
        else:
            raise AssertionError('Impossible hand type.')

    def higher_single(self, hand_to_beat):
        for card in sorted(self.cards):
            if card > hand_to_beat[0]:
                return [card.UI_suite_value]
        return False
    
    def higher_double(self, hand_to_beat):
        # Checking all pairwise combinations of cards in hand for a
        # double. 
        for card0, card1 in combinations(sorted(self.cards), 2):
            temp_hand = PresidentsHand([card0, card1])
            temp_hand.validate(print_message=False)
            if temp_hand.is_double and temp_hand > hand_to_beat:
                return [card.UI_suite_value for card in temp_hand.cards]
        return False

    def higher_triple(self, hand_to_beat):
        for card0, card1, card2 in combinations(sorted(self.cards), 3):
            temp_hand = PresidentsHand([card0, card1, card2])
            temp_hand.validate(print_message=False)
            if temp_hand.is_triple and temp_hand > hand_to_beat:
                return [card.UI_suite_value for card in temp_hand.cards]
        return False

    def higher_fullhouse(self, hand_to_beat):
         # First check for a triple that beats the hand to beat's
         # triple.
        for card0, card1, card2 in combinations(sorted(self.cards), 3):
            temp_hand = PresidentsHand([card0, card1, card2])
            temp_hand.validate(print_message=False)
            if temp_hand.is_triple and temp_hand > hand_to_beat.triple:
                temp_triple = temp_hand
                # If there is a double use it to create a fullhouse.
                remaining_cards = [card 
                                    for card in self.cards
                                    if card not in temp_hand]
                for card0, card1 in combinations(sorted(remaining_cards), 2):
                    temp_hand = PresidentsHand([card0, card1])
                    temp_hand.validate(print_message=False)
                    if temp_hand.is_double:
                        temp_double = temp_hand
                        temp_fullhouse = temp_triple + temp_double
                        temp_fullhouse.validate(print_message=False)
                        if temp_fullhouse > hand_to_beat:
                            return [card.UI_suite_value
                                    for card in temp_fullhouse.cards]
        return False
    
    def higher_straight(self, hand_to_beat):
        # The way I did this is horrible; need some algorithmic help here.abs
        for card0, card1, card2, card3, card4 in combinations(sorted(self.cards), 5):
            temp_hand = PresidentsHand([card0, card1, card2, card3, card4])
            temp_hand.validate(print_message=False)
            if temp_hand.is_straight and temp_hand > hand_to_beat:
                return [card.UI_suite_value for card in temp_hand.cards]
        return False

    def higher_bomb(self, hand_to_beat):
        # I just rushed this one, will come back and make smarter later...
        # The way I did this is horrible; need some algorithmic help here.abs
        for card0, card1, card2, card3, card4 in combinations(sorted(self.cards), 5):
            temp_hand = PresidentsHand([card0, card1, card2, card3, card4])
            temp_hand.validate(print_message=False)
            if temp_hand.is_bomb and temp_hand > hand_to_beat:
                return [card.UI_suite_value for card in temp_hand.cards]
        return False

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


class PresidentsSpot(Spot):
    """
    A class for presidents spots.
    """
    def __init__(self, table):
        if not isinstance(table, PresidentsTable):
            raise TypeError('Only PresidentsTables can have PresidentsSpots.')
        Spot.__init__(self, table)
        self.position = None
        self.reserve_time = 60 # will implement later...
        
    @property
    def has_3_of_clubs(self):
        return Card('c', '2') in self.cards

    def add_player(self, player):
        if not isinstance(player, PresidentsPlayer):
            raise TypeError(
                'Only PresidentsPlayers can hop into PresidentsSpots.')
        Spot.add_player(self, player)

    # I will explain this later...
    @property
    def can_play_anyhand(self):
        if self.has_3_of_clubs:
            return False
        winning_last = self.table.winning_last
        passes = self.table.passes_on_top
        players_left = self.table.players_left
        if winning_last and passes == players_left:
            return True
        elif winning_last:
            return False
        elif passes == players_left - 1:
            return True
        else:
            return False

    # Removes all cards and hands with any intersection with the hand
    # being played.
    def remove_intersecting(self, hand_to_play):
        for hand_card in hand_to_play:
            # Remove all hands containing any card in the hand being played
            self.hands[:] = [hand for hand in self.hands if hand_card not in hand]
            self.cards.remove(hand_card)    

    def __repr__(self):
        return f'PresidentsSpot(player:{self.player})'  


class Table:
    """
    Where players sit and play card games; holds instances of the Spot class.
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
            raise TypeError('Only instances of the CardGame class can be added as a game.')
        self.game = game
        self.game.table = self
    
    @property
    def deck(self):
        return self.game.deck

    def add_player(self, player):
        if not isinstance(player, Player):
            raise TypeError("Only instances of the Player class can be added to a table('s spot)")
        spot = self.open_spot
        if spot:
            spot.add_player(player)
        else:
            raise RuntimeError('Table has no open spots.')

    def remove_player(self, player):
        if not player in [spot.player for spot in self.spots]:
            raise RuntimeError('Player is not in any of the spots at the table.')

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


class PresidentsTable(Table):
    """
    class for a table that is already set up for presidents
    """
    def __init__(self, name='Presidents'):
        Table.__init__(self, name, num_spots=4, spot=PresidentsSpot)
        self.add_game(Presidents())

    def add_player(self, player):
        assert isinstance(player, PresidentsPlayer), 'Only PresidentsPlayers can sit at PresidentsTables.'
        Table.add_player(self, player)

    @property
    def passes_on_top(self):
        passes = 0
        for hand in self.played[::-1]:
            if isinstance(hand, PresidentsPass):
                passes += 1
            else:
                break
        assert 0 <= passes <= 3, 'Impossible number of passes played in a row.'
        return passes

    @property
    def last_played(self):
        passes = self.passes_on_top
        if passes == 0:
            return self.played[-1]
        elif passes == 1:
            return self.played[-2]
        elif passes == 2:
            return self.played[-3]
        elif passes == 3:
            return self.played[-4]

    # Returns whether the last played hand was a winning hand.
    @property
    def winning_last(self):
        return self.last_played.winning

    # Returns the number of players who have not exhausted their cards.
    @property
    def players_left(self):
        return sum([int(not spot.empty_handed) for spot in self.spots])

    def play(self, hand_to_play):
        assert isinstance(hand_to_play, PresidentsHand) or \
               isinstance(hand_to_play, PresidentsPass), \
               'This method can only be called by force_play_hand or pass_turn.'
        self.played.append(hand_to_play)
        self.game.update()        


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
            raise AssertionError(f'Impossible type ({type(cards)}) returned when indexing/slicing.')

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

    # subclasses of the Hand class must provide their own hand comparison criteria;
    # the alternative to this was requiring subclasses of the hand class to explicitly
    # enumerate all card combinations/permutations in order for the Hand class to 
    # then interpret, and even then, I'm not sure how it would handle comparison
    # rules, e.g. comparing hands of different sizes

    def __lt__(self, other):
        raise NotImplementedError('The < method must be provided by the subclass of the Hand class corresponding to the game being played.')

    def __le__(self, other):
        raise NotImplementedError('The <= method must be provided by the subclass of the Hand class corresponding to the game being played.')

    def __eq__(self, other):
        raise NotImplementedError('The == method must be provided by the subclass of the Hand class corresponding to the game being played.')

    def __ne__(self, other):
        raise NotImplementedError('The != method must be provided by the subclass of the Hand class corresponding to the game being played.')

    def __ge__(self, other):
        raise NotImplementedError('The >= method must be provided by the subclass of the Hand class corresponding to the game being played.')

    def __gt__(self, other):
        raise NotImplementedError('The > method must be provided by the subclass of the Hand class corresponding to the game being played.')

    
class PresidentsHand(Hand):
    """
    class for presidents hands
    """
    def __init__(self, cards=[], valid=False):
        if len(cards) > 5:
            raise RuntimeError('PresidentsHands can consist of 5 cards maximum.')
        for card0, card1 in combinations(cards, 2):
            if card0 == card1:
                raise RuntimeError('All cards in a presidents hand must be unique!')
        Hand.__init__(self, cards)
        self.valid = valid
        self.winning = False

    # validate and label presidents hand
    def validate(self, print_message=True):
        if self.valid:
            pass
        elif len(self) == 1:
            self.valid = True
            self.type = 'single'
            return
        elif len(self) == 2:
            if self.is_double:
                self.valid = True
                self.type = 'double'
        elif len(self) == 3:
            if self.is_triple:
                self.valid = True
                self.type = 'triple'
        elif len(self) == 4:
            # whether or not we implement quads is still up for debate
            # if self.is_quad:
            #     self.valid = True
            #     self.type = 'quad'
            pass
        elif len(self) == 5:
            if self.is_bomb:
                self.valid = True
                self.type = 'bomb'
            elif self.is_fullhouse:
                self.valid = True
                self.type = 'fullhouse'
            elif self.is_straight:
                self.valid = True
                self.type = 'straight'
        if print_message:
            self.validation_message()

    @property
    def is_double(self):
        assert len(self) == 2, 'Doubles consist of exactly 2 cards.'
        # if both cards have the same value, the hand is a double
        return self[0].same_value(self[1])

    @property
    def is_triple(self):
        assert len(self) == 3, 'Triples consist of exactly 3 cards.'
        # if the first two cards form a double and last two cards form a
        # double, the hand is triple
        return self[0:2].is_double and self[1:3].is_double

    # how quads are governed is still a hot topic of debate: in our regular play they
    # were always played with an extra card to make a bomb that beats everything except
    # higher bombs but how exactly should quads work if we don't really have a sample of 
    # people even using them because of the exsitence of bombs? 
    @property   
    def is_quad(self):
        assert len(self) == 4, 'Quads consist of exactly 4 cards.'
        # if the first three cards form a triple and the last two cards form a
        # double, the hand can be a quad
        return self[0:3].is_triple and self[2:4].is_double

    @property
    def is_fullhouse(self):
        assert len(self) == 5, 'Fullhouses consist of exactly 5 cards.'
        # sort the cards by value and create a hand using them
        sorted_hand = PresidentsHand(sorted(self))
        # since the cards are sorted by value, then either the first, middle, or last
        # three cards will be a triple if a triple exists
        triple_exists = False
        for i in range(3):
            if sorted_hand[i:i+3].is_triple:
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
            if remaining_hand.is_double:
                # save the triple for fullhouse comparisons
                self.triple = sorted_hand[i:i+3]
                self.triple.validate(print_message=False)
                return True
            else:
                return False

    @property
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
        
    @property
    def is_bomb(self):
        assert len(self) == 5, 'bombs consist of exactly 5 cards'
        # sort the cards by value and create a hand using them
        sorted_hand = PresidentsHand(sorted(self))
        # since the cards are sorted by value, then either the first or last
        # four cards being a quad will mean a bomb
        first_four = sorted_hand[0:4]
        last_four = sorted_hand[1:5]
        if first_four.is_quad:
            self.bomb_card = max(first_four)
            return True
        elif last_four.is_quad:
            self.bomb_card = max(last_four)
            return True
        else:
            return False

    def validation_message(self):
        if self.valid:
            print(f'{sorted(self)} is a valid {self.type} hand!')
        else:
            print(f'{sorted(self)} is not a valid presidents hand.')

    def comparison_check(self, other):
        if not (self.valid and other.valid):
            raise AssertionError('Only valid hands can be compared.')
        if not self.type == other.type:
            raise ValueError(f"You can't play a {self.type} on a {other.type}!")

    def __lt__(self, other):
        # Checking is a bomb is < to a non-bomb is trivial.
        if self.type == 'bomb' and other.type != 'bomb':
            return False
        if self.type != 'bomb' and other.type == 'bomb':
            return True
        self.comparison_check(other)
        if self.type == 'fullhouse':
            return self.triple < other.triple
        if self.type == 'bomb':
            return self.bomb_card < other.bomb_card
        return max([card for card in self.cards]) < max([card for card in other.cards])

    def __gt__(self, other):
        # Checking is a bomb is > to a non-bomb is trivial.
        if self.type == 'bomb' and other.type != 'bomb':
            return True
        if self.type != 'bomb' and other.type == 'bomb':
            return False
        self.comparison_check(other)
        if self.type == 'fullhouse':
            return self.triple > other.triple
        if self.type == 'bomb':
            return self.bomb_card > other.bomb_card
        return max([card for card in self.cards]) > max([card for card in other.cards])

    # PresidentsHands can never be equal to each other so if any of these calls
    # occur, there is a bug.
    
    def __le__(self, other):
        raise AssertionError('A <= call was made by a PresidentsHand.')

    def __eq__(self, other):
        raise AssertionError('A == call was made by a PresidentsHand.')

    def __ne__(self, other):
        raise AssertionError('A != call was made by a PresidentsHand.')

    def __ge__(self, other):
        raise AssertionError('A >= call was made by a PresidentsHand.')

    def __repr__(self):
        return f'PresidentsHand({[card for card in self.cards]})'


class CardGame:
    """
    generic card game class
    """
    def __repr__(self):
        'A card game'


class Presidents(CardGame):
    """
    Presidents card game class.
    """
    # 4 suites: clubs, diamonds, hearts, spades
    # Ordered from weakest to strongest.
    suite_order = ['c', 'd', 'h', 's']
    # 13 values: 2-10 (zero-indexed) and jack, queen, king, ace 
    # Ordered from weakest to strongest.
    # Values are zero-indexed, e.g. 1 is a 2, 2 is a 3, etc.; note that this is
    # only true in the application backend and database, all UI versions have
    # 1-1 card labels e.g. 3 of CLubs is 'c2' in the backend and database but
    # is 'c3' in all UI.
    value_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a', '1']
    # All cards arranged in order.
    # super odd error here: putting suite_order results in a name error seems
    # to break after the first for in the list comp, not sure if intended ???
    order = [PresidentsCard(j, i) for i in value_order for j in ['c', 'd', 'h', 's']]
    
    def __init__(self, rounds=1):
        self.rounds = rounds
        self.deck = Deck(self.order[:], 'Presidents')
        self.table = None
        self.current_spot = None

    @property
    def played(self):
        return self.table.played

    @property
    def current_player(self):
        return self.current_spot.player

    def play_game(self):
        if not self.table:
            raise RuntimeError('Presidents must be played at a table.')
        if not isinstance(self.table, PresidentsTable):
            raise TypeError('Presidents can only be played at a PresidentsTable.')
        if not all(self.table.players):
            raise RuntimeError(f'Presidents requires exactly 4 players; there are only {self.table.players}.')
        print('\nWelcome to Presidents!')
        for i in range(1,self.rounds+1):
            self.setup_round(i)
            self.play_round()
        print('\nTHANKS FOR PLAYING!')

    # there should be a separate function for determining the next spot that
    # can play a hand (the next spot that is not done), but it should be in
    # this function
    def play_round(self):
        while True:
            current_player = self.current_spot.player
            try:
                if not self.current_player.is_human:
                    self.current_player.play_or_pass()
                else:
                    pres_in = input(parse('<b,y,>pres> </b,y,>'))
                    pres_in_tokens = pres_in.split()
                    # all shortcuts will be methods of the Player class or one of its subclasses
                    shortcut = pres_in_tokens[0]
                    args = pres_in_tokens[1:]
                    func = self.current_player.func_lookup(shortcut)
                    if not func:
                        print(f"{shortcut} is not a valid command. Enter 'help' to see your options!")
                        continue
                    try:
                        if args:
                            func(*args)
                        else:
                            func()
                    except Exception as err:
                        print(err)
                        #raise
                if self.players_left == 1:
                    self.assign_position(asshole=True)
                    self.announce_position()
                    print('\nThe round is over! The results are as follows:')
                    self.announce_final_positions()
                    break
            except KeyboardInterrupt:
                print('\n\nKeyboardInterrupt')
                return
            except EOFError:
                print()
                return
            except AssertionError as err:
                print(err)
                raise

    def setup_round(self, round_num):
        self.table.clear_cards()
        self.table.clear_played()
        self.table.played.append(PresidentsStart())
        self.table.shuffle_deck()
        self.table.deal_cards()
        self.find_3_of_clubs()
        print()
        if round_num > 1:
            self.handle_card_swaps()
        self.report_turn()
    
    # update tells everyone that a hand has been played, if the hand played was
    # a winning hand (last card that the player had), the hand is labelled as
    # such and the position of the player is announced, finally the next player
    # is found and set as the current_spot
    def update(self):
        last = self.table.last
        if isinstance(last, PresidentsPass):
            print(f'{self.current_player} passed!')
        elif isinstance(last, PresidentsHand):
            print(f'{self.current_player} played a {last.type}: {sorted(last.cards)}')
        else:
            AssertionError('Impossible object added to played.')
        if self.current_spot.empty_handed:
            last.winning = True
            self.assign_position()
            self.announce_position()
        self.next_spot_with_cards()
        if self.players_left > 1:
            self.report_turn()
         
    # Iterates the instance spot generator until it hits the first spot with cards.
    def next_spot_with_cards(self):
        # First iterates once to go to the next spot at a minimum.
        self.current_spot = next(self.spot_cycler)
        while self.current_spot.empty_handed:
            self.current_spot = next(self.spot_cycler)

    # Finds the 3 of Clubs, sets the current spot to the one with the 3 of
    # clubs and creates and iterates the next_spot generator to the current player.
    def find_3_of_clubs(self):
        assert isinstance(self.table.last, PresidentsStart), 'Can only find the 3 of clubs at the beginning of the game.'
        for spot in self.table.spots:
            # remember, cards are zero-indexed in the backend and database, c2 is the 3 of Clubs
            if Card('c', '2') in spot.cards:
                self.current_spot = spot
                break
        print(f'{self.current_player} has the 3 of Clubs!')
        self.spot_cycler = self.table.spot_cycler()
        curr_spot = next(self.spot_cycler)
        # After this while loop, the instance spot cycler is on the spot with
        # the 3 of clubs
        while curr_spot is not self.current_spot:
            curr_spot = next(self.spot_cycler)

    def report_turn(self):
        if self.current_player.is_human:
            print(f"It's your turn, {self.current_player}! Enter 'help' to see your options!")
        else:
            print(f"It's {self.current_player}'s turn!")
        # the following lines are only for easing testing when playing against yourself...
        # self.current_player.view('all')
        # self.current_player.view('last')

    def handle_card_swaps(self):
        return

    @property
    def players_left(self):
        return self.table.players_left

    def assign_position(self, asshole=False):
        if asshole:
            self.current_spot.position = 'Asshole'
            return
        players_left = self.players_left
        if players_left == 3:
            self.current_spot.position = 'President'
        elif players_left == 2:
            self.current_spot.position = 'Vice President'
        elif players_left == 1:
            self.current_spot.position = 'Vice Asshole'
        else:
            raise AssertionError(f'Impossible number of players left: {players_left}.')

    def announce_position(self):
        print(f'{self.current_player} is {self.current_spot.position}!')

    def announce_final_positions(self):
        for position in ['President', 'Vice President', 'Vice Asshole', 'Asshole']:
            for spot in self.table.spots:
                if spot.position == position:
                    print(f'{position}: {spot.player}')

    def __repr__(self):
        return 'Presidents Game Instance'


class PresidentsStart:
    """
    Class for object that every presidents game starts with.
    """
    def __repr__(self):
        return 'Start'


class PresidentsPass:
    """
    Class for object that represents a passed turn in presidents.
    """
    def __repr__(self):
        return 'Pass'


@main
def quick_game(*names):
    print('Welcome to Single Player Command Line Presidents!')
    t = PresidentsTable()
    if not names:
        names = []
        names.append(input('What is your name? '))
        print('Who do you want to play presidents with?')
        for _ in range(3):
            names.append(input('Other Name: '))
    t.add_player(PresidentsPlayer(names[0]))
    for name in names[1:]:
        t.add_player(AIPresidentsPlayer(name))
    t.start_game()