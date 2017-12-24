from helpers import main
import random
from itertools import cycle


class Card:
    """
    A general class for cards in a standard 52-card deck. These cards need not
    be tied to any particular card game but some of their methods depend on the
    game they are being used for, namely, comparing cards with each other.  
    """
    suite_dict = {'c': 'Clubs', 'd': 'Diamonds', 'h': 'Hearts', 's': 'Spades'}
    # Note that the card values are zero-indexed to avoid having to store cards
    # with value 10 with an additional character. Although this slightly confusing
    # convention (you'll get used to it) is present in the backend and database,
    # all implementations of UI will present card values as one would expect.
    value_dict = {'1': '2', '2': '3', '3': '4', '4': '5', '5': '6', '6': '7',
                  '7': '8', '8': '9', '9': '10', 'j': 'Jack', 'q': 'Queen',
                  'k': 'King', 'a': 'Ace'}
    UI_to_BEDB_dict = {'2': '1', '3': '2', '4': '3', '5': '4', '6': '5',
                          '7': '6', '8': '7', '9': '8', '10': '9', 'j': 'j',
                          'q': 'q', 'k': 'k', 'a': 'a'}

    def __init__(self, suite, value):
        if not isinstance(suite, str):
            raise TypeError("Suites are the single letter strings: 'c', 'd', 'h', 's'.")
        if not isinstance(value, str):
            raise TypeError('Values must be given as strings, even for cards with numeric values.')
        if suite not in Card.suite_dict:
            raise ValueError("The only suites in the standard 52-card deck are: 'c', 'd', 'h', 's'.")
        if value not in Card.value_dict:
            raise ValueError('All values are zero-indexed, e.g. use 9 for 10, etc.')
        self.suite = suite
        self.value = value
        self.suite_value = self.suite + self.value

    def same_suite(self, other):
        return self.suite == other.suite

    def same_value(self, other):
        return self.value == other.value

    def same_card(self, other):
        return self.same_suite(other) and self.same_value(other)

    # Replace these methods if this basic equality definition must be expanded
    # or simply does not apply.
    def __eq__(self, other):
        return self.same_card(other)

    def __ne__(self, other):
        return not self == other
    
    # All other card comparison methods must be provided by the subclass of the
    # Card class corresponding to the game being played as rules dictating the
    # value of cards varies per card game.
    def __lt__(self, other):
        raise NotImplementedError('The < method must be provided by the subclass of the Card class corresponding to the game being played.')

    def __le__(self, other):
        raise NotImplementedError('The <= method must be provided by the subclass of the Card class corresponding to the game being played.')

    def __ge__(self, other):
        raise NotImplementedError('The > method must be provided by the subclass of the Card class corresponding to the game being played.')

    def __gt__(self, other):
        raise NotImplementedError('The >= method must be provided by the subclass of the Card class corresponding to the game being played.')

    def __repr__(self):
        suite = self.suite_dict[self.suite]
        value = self.value_dict[self.value]
        return f'{value} of {suite}'

    # Note the result of printing or str-ing a card returns its backend/
    # database representation (i.e. zero-indexed values for 2-10)
    def __str__(self):
        return self.suite_value

class PresidentsCard(Card):
    """
    A class for presidents cards, mainly dictating card comparisons.
    """
    # In order to compare a card with another, we need only compare each card's
    # position in the President's card order. The same follows for the greater
    # than method.
    def __lt__(self, other):
        return Presidents.order.index(self) < Presidents.order.index(other)

    def __gt__(self, other):
        self.same_game_assert(other)
        return Presidents.order.index(self) > Presidents.order.index(other)

    # Calls to <= and >= should never be made as they don't make sense in the
    # context of presidents
    def __le__(self, other):
        raise AssertionError('A <= call was made by a PresidentsCard.')

    def __ge__(self, other):
        raise AssertionError('A >= call was made by a PresidentsCard.')


class Deck:
    """
    A simple class for decks of cards.
    """
    # A deck is a list of Card objects
    def __init__(self, name='Standard', cards=[]):
        self.name = name
        # If a custom deck of cards is not provided:
        if not cards:
            # Default deck of cards is the standard 52-card deck.
            self.cards =\
                [Card(i, j) 
                    # 4 suites: clubs, diamonds, hearts, spades
                    for i in ['c', 'd', 'h', 's']
                    # 13 values: 2-10 (zero-indexed) and jack, queen, king, ace
                    for j in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a']]
        else:
            for card in cards:
                if not isinstance(card, Card):
                    raise TypeError('All cards in a deck must be Card objects.')
            self.cards = cards
    
    def shuffle(self):
        random.shuffle(self.cards)
        print('Deck has been shuffled.')
    
    # Generator that yields each card in the deck.
    @property
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
            raise TypeError('Players can only enter instances of the Spot class.')
        spot.add_player(self)

    def leave_spot(self):
        # In the future, this should send a request to the table to remove
        # the player from the table (at the next most appropriate time.)
        if not self.spot:
            raise RuntimeError('Player cannot leave a spot if they are not in one.')
        self.spot.remove_player()

    def create_hand(self):
        raise NotImplementedError('The create_hand method must be provided by the subclass of the Player class corresponding to the game being played.')

    def play_hand(self):
        raise NotImplementedError('The create_hand method must be provided by the subclass of the Player class corresponding to the game being played.')

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
            raise RuntimeError('Players must be in a spot to access hands and cards.')
        return self.spot.all

    def __repr__(self):
        return self.name


class PresidentsPlayer(Player):
    """
    class for presidents players
    """
    def __init__(self, name):
        Player.__init__(self, name)
        self.func_dict =\
        {   
            'view': (self.view,
                "'view cards': show cards\n            'view hands': show hands\n            'view all': show cards and hands\n            'view last': show last card played"),
            'hand': (self.create_hand,
                "use shorthand versions of card names separated by spaces to create a hand,\n            e.g. 'hand s2 h2 d2 c2 sa' creates a 2 bomb with an Ace of Spades"),
            'unhand': (self.unhand_hand,
                "deconstruct the hand at index i\n            i.e. 'unhand i' puts all the individual cards which made up the i-th hand back in your cards"),
            'play': (self.play_hand, 
                "play the hand at index i\n            i.e. 'play i' plays the i-th hand in hands\n            view hands and corresponding index with 'view hands'"),
            'pass': (self.pass_turn,
                'pass on the current hand being played on'),
            'help': (self.help,
                'list the command options and short descriptions of each'),
        }
        self.done = False
    
    def create_hand(self, *cards):
        # *cards should be comma separated UI suite_value strings (i.e the ones
        # that are NOT zero-indexed) of the cards desired in the hand.
        if not self.spot:
            raise RuntimeError('Player must be in a spot to create a hand.')
        # Convert the UI suite_value strings to backend/database suite_value
        # strings; this will KeyError if the the card value given is not valid.
        try:
            cards = [card[0]+self.game.UI_to_BEDB_dict[card[1:]] for card in cards]
        except KeyError:
            raise ValueError(f"{card[1:]} is not a valid card value; they are '2'-'10', 'j', 'q', 'k', 'a'.")
        # Convert suite_value strings to Card objects; this will ValueError if
        # if the card suite given is not valid; error message is included.
        cards_objs = map(lambda i, j: Card(i, j), cards)
        # Check that the player has the cards they want to make a hand using.
        desired_cards = []
        for card in cards_objs:
            if card not in self.cards:
                raise RuntimeError('The player does not have at least one of these cards.')
            else:
                desired_cards.append(card)
        desired_hand = PresidentsHand(desired_cards)
        if len(just_created) == 1:
            # No need to announce that a single is a valid hand.
            desired_hand.validate(print_message=False)
        else:
            desired_hand.validate(print_message=True)
        # Only valid hands should be added to the player('s spot)'s hands
        if desired_hand.valid:
            self.hands.append(desired_hand)
        
    def play_hand(self, hand_ind):
        if not self.spot:
            raise RuntimeError('Player must be in a spot to play a hand.')
        # Allow hands to be single card, UI suite_value strings and do the hand
        # building automatically
        if isinstance(hand_ind, str):
            # Check if hand_ind is a string with a valid suite for the first letter
            if hand_ind[0] in Presidents.suite_order:
                self.create_hand(hand_ind)
                # After creating the single card hand, try to play it.
                try:
                    self.play_hand(-1)
                # If it can't be played, unhand the created hand.
                except:
                    self.unhand_hand(-1)
                    raise # not sure about this raise
                return
        self.hand_ind_check(hand_ind)
        hand_to_play = self.hands[hand_ind]
        # if the hand wanting to played is not valid, attempt to validate it
        assert hand_to_play.valid, 'Invalid hands should not be able to get to this point.'
        last_played = self.table.last_played
        passes = self.table.passes_on_top
        if isinstance(last_played, PresidentsStart):
            assert Card('c','2') in hand_to_play, 'The starting hand must contain the 3 of Clubs.'
            # if the hand includes the 3 of clubs, remove the hand from the player's hands
            # and append it to the list of played cards
            self.force_play_hand(hand_ind, hand_to_play)
        else:
            if self.can_play_anyhand:
                self.force_play_hand(hand_ind, hand_to_play)
            else:
                if hand_to_play < last_played:
                    raise RuntimeError('This hand cannot beat the last.')
                self.force_play_hand(hand_ind, hand_to_play)

    def force_play_hand(self, hand_ind, hand_to_play=None):
        self.hand_ind_check(hand_ind)
        if not hand_to_play:
            hand_to_play = self.hands[hand_ind]
        self.hands.pop(hand_ind)
        self.table.played.append(hand_to_play)
        print(f'{self} played a {hand_to_play.type}: {sorted(hand_to_play)}')
        # if current player has no more hands or cards remaining, display his/her position
        # for next round and decrement the number of players remaining
        self.do_things_if_done()
        if self.game.players_left == 1:
            self.next_player(report=False)
        else:
            self.next_player()

    @property
    def can_play_anyhand(self):
        return self.spot.can_play_anyhand

    def unhand_hand(self, hand_ind):
        if hand_ind == 'all':
            self.unhand_all_hands()
            return
        self.hand_ind_check(hand_ind)
        self.hands.pop(hand_ind)
        
    def unhand_all_hands(self):
        for _ in range(len(self.hands)):
            self.hands.pop()

    def hand_ind_check(self, hand_ind):
        try:
            hand_ind = int(hand_ind)
        except:
            raise ValueError('Desired hand index must be an integer.')
        if len(self.hands) <= hand_ind:
            raise ValueError('There are not as many hands as you think.')
    
    def do_things_if_done(self):
        if self.all == []:
            self.done = True
            self.game.announce_position()
            self.game.players_left -= 1
            self.table.last_played.winning = True
    
    def next_player(self, report=True):
        # only used the magic method here so the method chaining would make sense
        self.game.current_player = self.game.next_player_gen.__next__()
        while self.game.current_player.done:
            self.game.current_player = self.game.next_player_gen.__next__()
        if report:
            self.game.report_turn()

    def pass_turn(self):
        assert self.game, 'Must be playing a game to play a hand.'
        assert self.table, 'Must be at a table to play cards.'
        assert not isinstance(self.table.played[-1], PresidentsStart), 'Cannot pass when you have the 3 of Clubs!'
        if self.table.last_played.winning and self.table.passes_on_top == self.game.players_left:
            print('No one beat the last hand, play any hand you want!')
        elif self.table.last_played.winning:
            self.table.played.append(PresidentsPass())
            print(f'{self} passed!')
            self.next_player()
        elif self.table.passes_on_top == self.game.players_left - 1:
            print('No one beat your last hand, play any hand you want!')
        else:
            self.table.played.append(PresidentsPass())
            print(f'{self} passed!')
            self.next_player()        
    
    def view(self, which):
        if which == 'all':
            self.view('cards')
            self.view('hands')
            # print(f'Hands: {[sorted(hand) for hand in self.hands]}\nCards: {sorted(self.cards)}')
        elif which == 'hands':
            for i, hand in enumerate(self.hands):
                print(f'{i}: {hand.cards}')
        elif which == 'cards':
            print(sorted(self.cards))
        elif which == 'last':
            if self.table.last_played.winning and self.table.passes_on_top == self.game.players_left:
                print(f'You can play any hand you want!')
            elif self.table.last_played.winning:
                print(f'What you have to beat: {self.table.last_played.cards}')
            elif self.table.passes_on_top == self.game.players_left - 1:
                print(f'You can play any hand you want!')
            else:
                print(f'What you have to beat: {self.table.last_played.cards}')
        else:
            print(f"{which} is not a valid argument for view. Enter 'help' to see your options")

    def help(self):
        for shortcut, info in self.func_dict.items():
            print(f'{shortcut.ljust(10)}: {info[1]}')

    def func_lookup(self, shortcut):
        # returns None if the function is not in the player function dictionary
        func = self.func_dict.get(shortcut)
        if func:
            return func[0]

    

class Spot:
    """
    A class for spots at a table.
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
        return self.hands + self.hands

    def add_player(self, player):
        if self.player:
            raise RuntimeError('Player must be removed from spot before another is added.')
        if not isinstance(player, Player):
            raise TypeError('Only instances of the Player class can be added to a spot.')
        self.player = player
        player.spot = self

    def remove_player(self):
        if not self.player:
            raise RuntimeError('Player cannot be removed if the spot does not have one.')
        self.player.spot = None
        self.player = None

    @property
    def empty_handed(self):
        return self.all == []

class PresidentsSpot:
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
            raise TypeError('Only PresidentsPlayers can hop into PresidentsSpots.')
        Spot.add_player(self, player)

    # I will explain this later...
    @property
    def can_play_anyhand(self):
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

class Table:
    """
    Where players sit and play card games; holds instances of the Spot class.
    """
    def __init__(self, num_spots=4, spot=Spot, name='Flavorless'):
        self.spots = []
        for _ in range(num_spots):
            self.spots.add_spot(spot(table=self))
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

    @property
    def spot_cycler(self):
        for spot in cycle(self.spots):
            yield spot

    def deal_cards(self):
        spot_cycler = cycle(self.spots.keys())
        dealer = self.deck.card_dealer()
        for card in dealer:
            next_spot = next(spot_cycler)
            self.cards[next_spot].append(card)
        print('Cards have been dealt.')

    # generator that yields the next player
    def next_player_gen(self):
        player_cycler = cycle(self.players)
        for player in player_cycler:
            yield player

    def start_game(self):
        self.game.play_game()

    @property
    def players(self):
        return self.spots.values()

    def __repr__(self):
        return f'{self.name} Table'


class PresidentsTable(Table):
    """
    class for a table that is already set up for presidents
    """
    def __init__(self, num_spots=4, spot=PresidentsSpot, name='Presidents'):
        Table.__init__(self, name)
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
        return sum([not spot.empty_handed for spot in self.spots])

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
        if cards == []:
            raise RuntimeError('invalid index')
        # Returns individual card if not slicing
        if not isinstance(cards, list):
            return cards
        return self.__class__(cards)

    def __len__(self):
        return len(self.cards)

    def __contains__(self, other):
        return other in self.cards
    
    def index(self, other):
        return self.cards.index(other)

    def __repr__(self):
        return f'Hand({[card for card in self.cards]})'

    # subclasses of the Hand class must provide their own hand comparison criteria;
    # the alternative to this was requiring subclasses of the hand class to explicitly
    # enumerate all card combinations/permutations in order for the Hand class to 
    # then interpret, and even then, I'm not sure how it would handle comparison
    # rules, e.g. comparing hands of different sizes
    
    
class PresidentsHand(Hand):
    """
    class for presidents hands
    """
    def __init__(self, cards=[], valid=False):
        assert len(cards) <= 5, 'PresidentsHands can consist of 5 cards maximum.'
        Hand.__init__(self, cards)
        # non-repeating pairwise comparison of cards in hand
        for i, card0 in enumerate(self.cards[:-1]):
            for card1 in self.cards[i+1:]:
                assert card0 != card1, 'All cards in a presidents hand must be unique.'
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
        if print_message:
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
            if remaining_hand.is_double():
                # save the triple for fullhouse comparisons
                self.triple = PresidentsHand(sorted_hand[i:i+3])
                self.triple.validate(print_message=False)
                return True
            else:
                return False

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
        first_four = sorted_hand[0:4]
        last_four = sorted_hand[1:5]
        if first_four.is_quad():
            self.bomb_card = max(first_four)
            return True
        elif last_four.is_quad():
            self.bomb_card = max(last_four)
            return True
        else:
            return False

    def validation_message(self):
        if self.valid:
            print(f'{sorted(self)} is a valid {self.type} hand!')
        else:
            print(f'{sorted(self)} is not a valid Presidents hand.')

    def comparison_assert(self, other):
        assert self.game is other.game, 'This requires both hands to be tied to the same game instance.'
        assert self.valid and other.valid, 'This requires both hands to be valid.'
        assert self.type == other.type, f"You can't play a {self.type} on a {other.type}!"

    # PresidentsHands can never be equal to each other

    def __lt__(self, other):
        # trivial bomb checks
        if self.type == 'bomb' and other.type != 'bomb':
            return False
        if self.type != 'bomb' and other.type == 'bomb':
            return True
        self.comparison_assert(other)
        if self.type == 'fullhouse':
            return self.triple < other.triple
        if self.type == 'bomb':
            return self.bomb_card < other.bomb_card
        return max([card for card in self.cards]) < max([card for card in other.cards])

    def __gt__(self, other):
        # trivial bomb checks
        if self.type == 'bomb' and other.type != 'bomb':
            return True
        if self.type != 'bomb' and other.type == 'bomb':
            return False
        self.comparison_assert(other)
        if self.type == 'fullhouse':
            return self.triple > other.triple
        if self.type == 'bomb':
            return self.bomb_card > other.bomb_card
        return max([card for card in self.cards]) > max([card for card in other.cards])

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
    
    def __init__(self, debug=False):
        self.rounds = 10
        # Using instance's order so class order will not be affected by shuffle.
        self.deck = Deck(self.order)
        self.table = None
        self.current_player = None

    def play_round(self):
        return

    @property
    def played(self):
        return self.table.played

    @property
    def finished(self):
        # players_w_no_cards = 0
        # for cards in self.table.
        return True

    def play_game(self):
        assert self.table.played == [], 'Cannot start a game if cards have already been played.'
        assert all(self.table.spots.values()), 'Playing Presidents requires exactly 4 players.'
        self.players_left = 4
        print('\nWelcome to Presidents!')
        self.setup_table()
        self.find_3_of_clubs()
        self.next_player_gen = self.table.next_player_gen()
        # cycle through the next player generator until hitting the player identified
        # to have the 3 of Clubs from above
        current_gen_player = next(self.next_player_gen)
        while current_gen_player is not self.current_player:
            current_gen_player = next(self.next_player_gen)
        self.report_turn()
        self.game_loop()


    def find_3_of_clubs(self):
        assert isinstance(self.table.played[-1], PresidentsStart), 'Can only find the 3 of clubs at the beginning of the game.'
        for spot, player in self.table.spots.items():
            # remember, cards are zero-indexed in the backend and database, c2 is the 3 of Clubs
            if Card('c', '2') in self.table.cards[spot]:
                self.current_player = player
        print(f'{self.current_player.name} has the 3 of Clubs!')
        
    def report_turn(self):
        print(f"It's your turn, {self.current_player}! Enter 'help' to see your options!")

    def setup_table(self):
        self.table.played.append(PresidentsStart())
        self.table.shuffle_deck()
        self.table.deal_cards()

    def game_loop(self):
        while True:
            try:
                pres_in = input('pres> ')
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
                    print("Make sure arguments are in the correct form! Enter 'help' to check out the forms!")
                    if self.debug:
                        raise
                if self.players_left == 1:
                    self.announce_position()
                    print(f'\nThe game is over! The results are as follows:')
                    print(f'President: {self.positions[0]}')
                    print(f'Vice President: {self.positions[1]}')
                    print(f'Vice Asshole: {self.positions[2]}')
                    print(f'Asshole: {self.positions[3]}')
                    print('\nTHANKS FOR PLAYING!')
                    break
            except KeyboardInterrupt:
                print('\n\nKeyboardInterrupt')
                return
            except EOFError:
                print()
                return
            except AssertionError as err:
                print(err)
            # except Exception as err:
            #     print(f"The following error might not make sense, but you might be able to use it to tell what's wrong!\n{err}")

    def announce_position(self):
        if self.players_left == 4:
            print(f'Congratulations {self.current_player}! You are President!')
        elif self.players_left == 3:
            print(f'Great work {self.current_player}! You are Vice President!')
        elif self.players_left == 2:
            print(f'Good work {self.current_player}! You are Vice Asshole!')
        elif self.players_left == 1:
            print(f'Sorry {self.current_player}! You are Asshole!')
        else:
            raise AssertionError('impossible number of players left')
        self.positions.append(self.current_player)

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

# @main
# def quick_game(debug=False):
#     print('Welcome to Single Player Command Line Presidents!')
#     t = PresidentsTable()
#     if debug:
#         t.game.debug = True
#     name = input('What is your name? ')
#     print('Who do you want to play presidents with?')
#     other_names = [input('Other Name: '), input('Other Name: '), input('Other Name: ')]
#     for name in [name] + other_names:
#         PresidentsPlayer(name).join_table(t)
#     t.start_game()