from helpers import main
from random import shuffle as rand_shuffle
from itertools import cycle

class Card:
    """
    class for cards and card comparisons
    """
    suite_dict = {'c': 'Clubs', 'd': 'Diamonds', 'h': 'Hearts', 's': 'Spades'}
    # value_dict = {'1': 'Two', '2': 'Three', '3': 'Four', '4': 'Five', '5': 'Six',
    #                '6': 'Seven', '7': 'Eight', '8': 'Nine', '9': 'Ten', 'j': 'Jack',
    #                'q': 'Queen', 'k': 'King', 'a': 'Ace'}
    value_dict = {'1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 9,
                  '9': 10, 'j': 'Jack', 'q': 'Queen', 'k': 'King', 'a': 'Ace'}

    def __init__(self, suite, value, game=None):
        self.suite = suite
        self.value = value
        self.suite_value = self.suite + self.value
        self.game = game

    def same_suite(self, other):
        return self.suite == other.suite

    def same_value(self, other):
        return self.value == other.value

    def game_assert(self, other):
        assert self.game, 'This method requires a card tied to a game.'
        assert other.game, 'This method requires a card tied to a game.'
        assert self.game is other.game, 'This method requires both cards to be tied to the same game instance.'

    def __lt__(self, other):
        self.game_assert(other)
        # convert the game's order to a (invalid) Hand so we can check if
        # the card is in the list of game cards; this method follows for
        # the rest of the comparisons 
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) < game_cards_hand.index(other)

    def __le__(self, other):
        self.game_assert(other)
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) <= game_cards_hand.index(other)

    def __eq__(self, other):
        self.game_assert(other)
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) == game_cards_hand.index(other)

    def __ne__(self, other):
        self.game_assert(other)
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) != game_cards_hand.index(other)

    def __ge__(self, other):
        self.game_assert(other)
        game_cards_hand = Hand(self.game.order) 
        return game_cards_hand.index(self) >= game_cards_hand.index(other)

    def __gt__(self, other):
        self.game_assert(other)
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
                    for j in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a']]
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
    def __init__(self, name): #, spot=None, table=None, game=None):
        self.name = name
        # for now, you can't automatically 'spawn' players onto a table and must
        # manually add them to a table, but will add in the future
        self.spot = None
        self.table = None
        self.game = None

    # adds player to a table if there is an open spot
    # will add functionality for spectating in the future
    def join_table(self, table):
        table.add_player(self)

    def leave_table(self, table):
        table.remove_player(self)

    def create_hand(self, *cards):
        # *cards should be a comma separated list of suite_value strings of the
        # cards desired in the hand
        assert self.table, 'Must be at a table to create a hand'
        assert self.game, 'Must be playing a game to create a hand'
        suites_values = [card.suite_value for card in self.cards]
        hand_indeces = []
        # use suite_value's of each card to check if the player is creating a
        # hand using cards that they actually have
        for card in cards:
            assert card in suites_values, 'Card must be in your cards'
            hand_indeces.append(suites_values.index(card))
        # step through a reversed sorted version of the indeces so smaller
        # indeces remain intact while popping larger ones
        desired_cards = []
        for i in sorted(hand_indeces, reverse=True):
            desired_cards.append(self.cards.pop(i))
        # create a hand using the type of hand that the game provides
        desired_hand = self.game.hand(desired_cards)
        self.hands.append(desired_hand)
        
    def remove_from_hand(self, hand_ind, to_remove):
        return

    def add_to_hand(self, hand_ind, to_add):
        return

    def unhand_hand(self, hand_ind):
        popped_hand = self.hands.pop(hand_ind)
        while popped_hand.cards:
            self.cards.append(popped_hand.cards.pop())
     
    def unhand_all_hands(self):
        for i in reversed(range(len(self.hands))):
            self.unhand_hand(i)

    def validate_hands(self):
        for hand in self.hands:
            hand.validate()

    @property
    def last_played(self):
        assert self.table, 'Must be at a table to view hands'
        return self.table.played[-1]

    @property
    def hands(self):
        assert self.table, 'Must be at a table to view hands'
        return self.table.hands[self.spot]

    @property
    def cards(self):
        assert self.table, 'Must be at a table to view non-hands'
        return self.table.cards[self.spot]

    @property
    def all(self):
        assert self.table, 'Must be at a table to view all cards'
        return self.table.hands[self.spot] + self.table.cards[self.spot]

    def __repr__(self):
        return f'{self.name}'


class PresidentsPlayer(Player):
    """
    class for presidents players
    """
    def __init__(self, name):
        Player.__init__(self, name)
        self.func_dict =\
        {   
            'hand': (self.create_hand, "use shorthand versions of card names separated by spaces to create a hand, e.g. `hand s2 h2 d2 c2 sa'"),
            'view': (self.view, "look at both your hands and individual cards with 'view all' and look at them seperately with 'view hands' and 'view cards', respectively"),
            'help': (self.help, 'list the command options and short descriptions of each')
        }
        self.done = False

    def play_hand(self, hand_ind):
        assert self.game, 'Must be playing a game to play a hand.'
        assert self.table, 'Must be at a table to play cards.'
        assert len(self.hands) > hand_ind, 'There are not as many hands as you think.'
        hand_to_play = self.hands[hand_ind]
        # if the hand wanting to played is not valid, attempt to validate it
        if not hand_to_play.valid:
            hand_to_play.validate()            
            assert hand_to_play.valid, 'Can only play valid hands'
        top_of_played = self.table.played[-1]
        if isinstance(top_of_played, PresidentsStart):
            assert Card('c','2') in hand_to_play, 'The starting hand must contain the 3 of Clubs.'
            # if the hand includes the 3 of clubs, remove the hand from the player's hands
            # and append it to the list of played cards
            self.force_play_hand(hand_ind, hand_to_play)
        # handle multiple numbers of passes
        # if there are 1 or 2 passes at the top of the played cards, the player must beat
        # the card before the passes
        # if there are 3 passes, all players have passed and the current player is allowed
        # to play any hand
        elif isinstance(top_of_played, PresidentsPass):
            before_top = self.table.played[-2]
            # if the top card is a Pass, check if the previous one was also a pass
            if isinstance(before_top, PresidentsPass):
                before_before_top = self.table.played[-3]
                # the card before the top card is a pass, check if the card before that
                # was also a pass
                if isinstance(before_before_top, PresidentsPass):
                    # if there are 3 passes in a row, the current player is allowed to play
                    # any hand that they want
                    self.force_play_hand(hand_ind, hand_to_play)
                # if there are only 2 passes in a row, then the current player must beat the
                # card below the 2 passes
                else:
                    assert hand_to_play > before_before_top, 'This hand cannot beat the last!'
                    self.force_play_hand(hand_ind, hand_to_play)
            # if there is only one pass, then the current player must beat the card below
            # the pass
            else:
                assert hand_to_play > before_top, 'This hand cannot beat the last!'
                self.force_play_hand(hand_ind, hand_to_play)
        # if the last card played is neither a Start or a Pass, simply try to beat it
        else:
            assert hand_to_play > top_of_played, 'This hand cannot beat the last!'
            self.force_play_hand(hand_ind, hand_to_play)

    def force_play_hand(self, hand_ind, hand_to_play=None):
        if not hand_to_play:
            hand_to_play = self.hands[hand_ind]
        self.hands.pop(hand_ind)
        self.table.played.append(hand_to_play)
        # if current player has no more hands or cards remaining, display his/her position
        # for next round and decrement the number of players remaining
        if self.current_player.all == []:
            self.current_player.done = True
            self.game.announce_position()
            self.game.players_left -= 1
        # only used the magic method here so the method chaining would make sense
        while self.game.current_player.done:
            self.game.current_player = self.game.next_player_gen.__next__()
        
    def view(self, which):
        if which == 'all':
            print(f'Hands: {self.hands}\nCards: {sorted(self.cards)}')
        elif which == 'hands':
            print(sorted(self.hands))
        elif which == 'cards':
            print(sorted(self.cards))

    def help(self):
        for shortcut, info in self.func_dict.items():
            print(f'{shortcut}: {info[1]}')

    def func_lookup(self, shortcut):
        # returns None if the function is not in the player function dictionary
        func = self.func_dict.get(shortcut)
        if func:
            return func[0]

        
class Table:
    """
    Where players sit and play card games.
    """
    def __init__(self, name='Flavorless'): #, game=None, deck=None):
        self.name = name
        # similarly to players, can't make table which comes with a game and 
        # deck attached and must manually add them; might add later
        self.game = None
        self.spots = {1: None, 2:None, 3:None, 4:None}
        # cards key corresponds to spots keys
        self.cards = {1: [], 2: [], 3: [], 4:[]}
        # hands key corresponds to spots keys
        self.hands = {1: [], 2: [], 3: [], 4:[]}
        self.played = []
        
    def add_game(self, game):
        self.game = game
        self.game.table = self
    
    @property
    def deck(self):
        return self.game.deck

    def add_player(self, player):
        open_spot = self.has_space()
        if open_spot:
            player.table = self
            self.spots[open_spot] = player
            player.spot = open_spot
            if self.game:
                player.game = self.game
        else:
            print('Table has not open spots.')

    def remove_player(self, player):
        assert player.table is self, 'Player must be at a table to leave it.'
        # player can leave the table while keeping the cards in that spot intact
        self.spots[player.spot] = None
        player.spot = None
        player.table = None
        player.game = None

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
    def __init__(self, name='Presidents'):
        Table.__init__(self, name)
        self.add_game(Presidents())

    def add_player(self, player):
        assert isinstance(player, PresidentsPlayer), 'Only PresidentsPlayers can sit at PresidentsTables.'
        Table.add_player(self, player)


class Hand:
    """
    simple Class for card hands
    """
    # a hand is a list of Card objects
    def __init__(self, cards=[]):
        
        for card in cards:
            assert isinstance(card, Card), 'All cards in a hand must be Card objects.'
        if cards:
            game = cards[0].game
            for card in cards:
                assert card.game is game, 'All cards must be part of the same game instance.'
            self.game = game
        else:
            self.game = None
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
    
    # indexing into Hands allows for comparing cards that are not tied to the same
    # game instance
    def index(self, other):
        if other in self:
            for i, card in enumerate(self.cards):
                if card.same_suite(other) and card.same_value(other):
                    return i
        else:
            raise IndexError('Card is not in hand.')

    def __repr__(self):
        return f'Hand({[card for card in self.cards]})'

    # children of the Hand class must provide their own hand comparison criteria;
    # the alternative to this was requiring children of the hand class to explicitly
    # enumerate all card combinations/permutations in order for the Hand class to 
    # then interpret, and even then, I'm not sure how it would handle comparison
    # rules, e.g. comparing hands of different sizes
    
    
class PresidentsHand(Hand):
    """
    class for presidents hands
    """
    def __init__(self, cards=[]):
        assert len(cards) <= 5, 'PresidentsHands can consist of 5 cards maximum.'
        Hand.__init__(self, cards)
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

    def comparison_assert(self, other):
        assert self.game is other.game, 'This method requires both hands to be tied to the same game instance.'
        assert self.valid and other.valid, 'This method requires both hands to be valid.'
        assert self.type == self.type, 'This method requires both hands to have the type.'

    def __lt__(self, other):
        self.comparison_assert(other)
        return max([card for card in self.cards]) < max([card for card in other.cards])

    def __gt__(self, other):
        self.comparison_assert(other)
        return max([card for card in self.cards]) > max([card for card in other.cards])

    def __repr__(self):
        return f'PresidentsHand({[card for card in self.cards]})'
    
class Presidents:
    """
    Presidents card game class, contains idk.
    """
    # 4 suites: clubs, diamonds, hearts, spades
    # ordered from weakest to strongest
    suite_order = ['c', 'd', 'h', 's']
    # 13 values: 2-10 (zero-indexed) and jack, queen, king, ace 
    # ordered from weakest to strongest
    # values are zero-indexed, e.g. 1 is a 2, 2 is a 3, etc.; note that this is only true
    # in the application backend and database, all UI versions have 1-1 card labels
    # e.g. 3 of CLubs is 'c2' in the backend and database but is 'c3' in all UI
    value_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'j', 'q', 'k', 'a', '1']
    print(suite_order)
    order = [Card(j, i) for i in value_order
                        # super odd error here: putting suite_order results in a name error
                        # seems to break after the first for in the list comp, not sure if intended
                        for j in ['c', 'd', 'h', 's']] 
    hand = PresidentsHand
    
    def __init__(self):
        # president's card deck, with cards ordered from weakest to strongest
        self.deck = Deck('Presidents',
                         [Card(j, i, self) for i in self.value_order 
                                           for j in self.suite_order])
        # might add ability to start a game with table included
        self.table = None
        self.current_player = None


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
            if Card('c', '2', self) in self.table.cards[spot]:
                self.current_player = player
        print(f'{self.current_player.name} has the 3 of Clubs!')
        
    def report_turn(self):
        print(f"It's your turn, {self.current_player}! Enter help to see your options!")

    def setup_table(self):
        self.table.shuffle_deck()
        self.table.deal_cards()
        self.table.played.append(PresidentsStart())

    def game_loop(self):
        while True:
            try:
                hands_played = len(self.played)
                pres_in = input('pres> ')
                pres_in_tokens = pres_in.split()
                # all shortcuts will be methods of the Player class or one of its subclasses
                shortcut = pres_in_tokens[0]
                args = pres_in_tokens[1:]
                func = self.current_player.func_lookup(shortcut)
                if not func:
                    print(f'{shortcut} is not a valid command. Enter help to see your options!')
                    break
                if args:
                    func(*args)
                else:
                    func()
                if self.players_left == 1:
                    self.announce_position()
                # if the function added a hand (or a pass) to the deck, tell the next player
                # that its their turn
                if hands_played < len(self.played) and self.players_left > 1:
                    self.report_turn()                                
            except KeyboardInterrupt:
                print('\n\nKeyboardInterrupt')
                return
            except EOFError:
                print()
                return
            except Exception as err:
                print(f"The following error might not make sense, but you might be able to use it to tell what's wrong!\n{err}")

    def announce_position(self):
        if self.players_left == 4:
            print(f'Congratulations {self.current_player}! You are President!')
        elif self.players_left == 3:
            print(f'Great work {self.current_player}! You are Vice President!')
        elif self.players_left == 2:
            print(f'Good work {self.current_player}! You are Vice Asshole!')
        elif self.players_left == 1:
            print(f'Sorry {self.current_player}! You are Asshole!')

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












t = PresidentsTable()
a = PresidentsPlayer('Adam')
b = PresidentsPlayer('Bobby')
c = PresidentsPlayer('Collin')
d = PresidentsPlayer('Dave')
for i in [a, b, c, d]:
    i.join_table(t)
t.start_game()

p = Presidents()
p0 = Presidents()
p1 = Presidents()
h = Hand([Card('c', 'k', p),
                    Card('d', '9', p),
                    Card('h', '8', p),
                    Card('s', '4', p),
                    Card('c', '5', p),
                    Card('c', '1', p),
                    Card('d', '2', p),
                    Card('h', '3', p),
                    Card('s', '4', p),
                    Card('c', '6', p)])

j = PresidentsHand([Card('c', '9', p0),
                    Card('d', '9', p0)])

k = PresidentsHand([Card('s', '1', p0),
                    Card('h', '1', p0)])