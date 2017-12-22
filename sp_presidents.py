from helpers import main
from random import shuffle as rand_shuffle
from itertools import cycle

class Card:
    """
    class for cards and card comparisons
    """
    suite_dict = {'c': 'Clubs', 'd': 'Diamonds', 'h': 'Hearts', 's': 'Spades'}
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
        try:
            desired_hand = self.game.hand(desired_cards)
        # if the creation of the hand fails, append the cards back into the player's cards
        except:
            for card in desired_cards:
                self.cards.append(card)
                raise           
        # if the hand is successfully created, add it to the player's hands
        self.hands.append(desired_hand)
        
    def remove_from_hand(self, hand_ind, to_remove):
        hand_ind = int(hand_ind)
        assert len(self.hands) > hand_ind, 'There are not as many hands as you think.'
        return

    def add_to_hand(self, hand_ind, to_add):
        hand_ind = int(hand_ind)
        assert len(self.hands) > hand_ind, 'There are not as many hands as you think.'
        return

    def unhand_hand(self, hand_ind):
        hand_ind = int(hand_ind)
        assert len(self.hands) > hand_ind, 'There are not as many hands as you think.'
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
    def hands(self):
        assert self.table, 'Must be at a table to view hands'
        return self.table.hands[self.spot]

    @property
    def cards(self):
        assert self.table, 'Must be at a table to view non-hands'
        return self.table.cards[self.spot]

    # this is for debugging
    @cards.setter
    def cards(self, val):
        assert self.table, 'Must be at a table to view non-hands'
        self.table.cards[self.spot] = val

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
        self.post_bombing = False
    
    def create_hand(self, *cards):
        cards = [card[0]+self.game.UI_to_backend_dict[card[1:]] for card in cards]
        Player.create_hand(self, *cards)
        # check if the hand just added to hands is a valid president's hand, if not, unhand it
        just_created = self.hands[-1]
        just_created.validate()
        if not just_created.valid:
            self.unhand_hand(-1)
        
    def play_hand(self, hand_ind):
        assert self.game, 'Must be playing a game to play a hand.'
        assert self.table, 'Must be at a table to play cards.'
        # allow hands to be single card shorthand strings and do the hand building automatically
        # check if hand_ind is a string with a suite shorthand for the first letter
        if isinstance(hand_ind, str):
            if hand_ind[0] in self.game.suite_order:
                self.create_hand(hand_ind)
            # # if suite and value are accidentally switched for single card plays
            # elif hand_ind[-1] in self.game.suite_order:
            #     self.create_hand(hand_ind[1:]+hand_ind[0])
            # after creating the single card hand, try to play it
            try:
                self.play_hand(-1)
            # if it can't be played, unhand the created hand
            except:
                self.unhand_hand(-1)
                raise
            return
        hand_ind = int(hand_ind)
        assert len(self.hands) > hand_ind, 'There are not as many hands as you think!'
        hand_to_play = self.hands[hand_ind]
        # if the hand wanting to played is not valid, attempt to validate it
        if not hand_to_play.valid:
            hand_to_play.validate()            
            assert hand_to_play.valid, 'Can only play valid hands.'
        top_of_played = self.table.played[-1]
        passes = self.table.passes_on_top
        if isinstance(top_of_played, PresidentsStart):
            assert Card('c','2') in hand_to_play, 'The starting hand must contain the 3 of Clubs.'
            # if the hand includes the 3 of clubs, remove the hand from the player's hands
            # and append it to the list of played cards
            self.force_play_hand(hand_ind, hand_to_play)
        # if there is only one pass, then the current player must beat the card below the pass
        elif passes == 1:
            before_top = self.table.played[-2]
            assert hand_to_play > before_top, 'This hand cannot beat the last! (1)'
            self.force_play_hand(hand_ind, hand_to_play)
        # if there are only 2 passes in a row, then the current player must beat the card 
        # below the 2 passes
        elif passes == 2:
            before_before_top = self.table.played[-3]
            assert hand_to_play > before_before_top, 'This hand cannot beat the last! (2)'
            self.force_play_hand(hand_ind, hand_to_play)
        # if there are 3 passes in a row, the current player is allowed to play any hand 
        # that they want
        elif passes == 3:
            self.force_play_hand(hand_ind, hand_to_play)
        # if the last card played is neither a Start or a Pass, simply try to beat it
        else:
            if not self.post_bombing:
                assert hand_to_play > top_of_played, 'This hand cannot beat the last! (3)'
            # if the player is playing a hand post-bombing, force the hand played
            else:
                self.post_bombing = False
            self.force_play_hand(hand_ind, hand_to_play)

    def force_play_hand(self, hand_ind, hand_to_play=None):
        if not hand_to_play:
            hand_to_play = self.hands[hand_ind]
        self.hands.pop(hand_ind)
        self.table.played.append(hand_to_play)
        print(f'{self} played a {hand_to_play.type}: {sorted(hand_to_play)}')
        # if current player has no more hands or cards remaining, display his/her position
        # for next round and decrement the number of players remaining
        self.announce_pos_if_done()
        if hand_to_play.type == 'bomb':
            self.post_bombing = True
            print(f"It's your turn again, {self}! Enter 'help' to see your options!")
        else:
            if self.game.players_left == 1:
                return
            self.next_player()
    
    def announce_pos_if_done(self):
        if self.all == []:
            self.done = True
            self.game.announce_position()
            self.game.players_left -= 1
    
    def next_player(self):
        # only used the magic method here so the method chaining would make sense
        self.game.current_player = self.game.next_player_gen.__next__()
        while self.game.current_player.done:
            self.game.current_player = self.game.next_player_gen.__next__()
        self.game.report_turn()

    def pass_turn(self):
        assert self.game, 'Must be playing a game to play a hand.'
        assert self.table, 'Must be at a table to play cards.'
        assert not isinstance(self.table.played[-1], PresidentsStart), 'Cannot pass when you have the 3 of Clubs!'
        assert self.table.passes_on_top < 3, 'No one beat your last hand, play any hand you want!'
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
            if self.post_bombing or self.table.passes_on_top == 3:
                print(f'You can play any hand you want!')
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

    @property
    def passes_on_top(self):
        passes = 0
        # only check the top 3 cards that have been played
        for hands in self.played[-1:-4:-1]:
            if isinstance(hands, PresidentsPass):
                passes += 1
            else:
                break
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
    def __init__(self, cards=[], valid=False):
        assert len(cards) <= 5, 'PresidentsHands can consist of 5 cards maximum.'
        Hand.__init__(self, cards)
        # non-repeating pairwise comparison of cards in hand
        for i, card0 in enumerate(self.cards[:-1]):
            for card1 in self.cards[i+1:]:
                assert card0 != card1, 'All cards in a presidents hand must be unique.'
        self.valid = valid

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
    order = [Card(j, i) for i in value_order
                        # super odd error here: putting suite_order results in a name error
                        # seems to break after the first for in the list comp, not sure if intended
                        for j in ['c', 'd', 'h', 's']] 
    hand = PresidentsHand
    UI_to_backend_dict = {'2': '1', '3': '2', '4': '3', '5': '4', '6': '5', '7': '6', '8': '7',
                          '9': '8', '10': '9', 'j': 'j', 'q': 'q', 'k': 'k', 'a': 'a'}
    
    def __init__(self, debug=False):
        self.debug = debug
        # president's card deck, with cards ordered from weakest to strongest
        self.deck = Deck('Presidents',
                         [Card(j, i, self) for i in self.value_order 
                                           for j in self.suite_order])
        # might add ability to start a game with table included
        self.table = None
        self.current_player = None
        self.positions = []

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
            if Card('c', '2', self) in self.table.cards[spot]:
                self.current_player = player
        print(f'{self.current_player.name} has the 3 of Clubs!')
        
    def report_turn(self):
        print(f"It's your turn, {self.current_player}! Enter 'help' to see your options!")

    def setup_table(self):
        self.table.shuffle_deck()
        self.table.deal_cards()
        self.table.played.append(PresidentsStart())

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

@main
def quick_game(debug=False):
    print('Welcome to Single Player Command Line Presidents!')
    t = PresidentsTable()
    if debug:
        t.game.debug = True
    name = input('What is your name? ')
    print('Who do you want to play presidents with?')
    other_names = [input('Other Name: '), input('Other Name: '), input('Other Name: ')]
    for name in [name] + other_names:
        PresidentsPlayer(name).join_table(t)
    t.start_game()

# print('Welcome to Single Player Command Line Presidents!')
# t = PresidentsTable()
# name = input('What is your name? ')
# print('Who do you want to play presidents with?')
# other_names = [input('Other Name: '), input('Other Name: '), input('Other Name: ')]
# for name in [name] + other_names:
#     PresidentsPlayer(name).join_table(t)
# t.start_game()