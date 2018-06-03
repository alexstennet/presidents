from hand import Hand, DuplicateCardError, FullHandError
from card_hand_chamber import CardHandChamber
from hand_list import HandList
from flask import request, session, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from typing import Dict, List, Generator
from itertools import cycle
import numpy as np

# TODO: get rid of all the ".get"s
# TODO: figure out how the imports are working lol
# TODO: how to organize helper functions--maybe a different file entirely?
# TODO: move client updates up as early as possible
# TODO: change hand list in session to "stored hands"
# TODO: generally clean the fuck out of this plz wow
# TODO: doing the whole global thing?
# TODO: is this the "server"?
# TODO: encapsulate all the below in a Game class?
# TODO: make sure only socket events access the session or request
# TODO: order functions
# TODO: it looks like broadcast false is equivalent to room player sid
# TODO: server should tell current player "it's your turn!"

# TODO: where to put these
current_hand_dict: Dict[str, Hand] = dict()
# TODO: should not be a dict from sid so another player can take over
card_hand_chamber_dict: Dict[str, CardHandChamber] = dict()
hand_in_play_dict: Dict[str, Hand] = dict()
player_sids_dict: Dict[str, List[str]] = dict()
player_cycler_dict: Dict[str, Generator[str, None, None]] = dict()
current_player_dict: Dict[str, str] = dict()
finished_player_sids_dict: Dict[str, List[str]] = dict()
num_unfinished_players_dict: Dict[str, int] = dict()
consecutive_passes_dict: Dict[str, int] = dict()
names_dict: Dict[str, str] = dict()


position_dict: Dict[int, str] = {
    1: 'asshole',
    2: 'vice asshole', 
    3: 'vice president',
    4: 'president'
}


def get_room() -> str:
    return session['room']


def get_name() -> str:
    return session['name']


def get_sid() -> str:
    return request.sid


def get_current_hand(player_sid):
    return current_hand_dict[player_sid]


def get_card_hand_chamber(player_sid):
    return card_hand_chamber_dict[player_sid]


def get_hand_in_play(room):
    return hand_in_play_dict[room]


@socketio.on('text', namespace='/presidents')
def text(message):
    room = get_room()
    name = get_name()
    emit('message', {'msg': f"{name}: {message['msg']}"}, room=room)


@socketio.on('joined', namespace='/presidents')
def joined(message):
    room = get_room()
    name = get_name()
    player_sid = get_sid()
    join_room(room)
    add_player(room, name, player_sid)
    emit('status', {'msg': f"{name}" + ' has entered the room.'}, room=room)
    if len(player_sids_dict[room]) == 4:
        start_game(room)


def add_player(room, name, player_sid):
    names_dict[player_sid] = name
    player_sids = player_sids_dict[room] = player_sids_dict.get(room, list())
    player_sids.append(player_sid)
    current_hand_dict[player_sid] = Hand()


# TODO: don't really like this but like wut do
class Start:  # for playing the 3 of clubs on 
    pass
Start = Start()


def start_game(room):
    deal_cards_and_establish_turn_order(room)
    hand_in_play_dict[room] = Start
    finished_player_sids_dict[room] = list()
    num_unfinished_players_dict[room] = 4
    consecutive_passes_dict[room] = 0


def deal_cards_and_establish_turn_order(room):
    deck = np.arange(1, 53)
    np.random.shuffle(deck)
    decks = deck.reshape(4, 13)
    decks.sort(axis=1)  # sorts each deck
    c3_index = np.where(decks == 1)[0][0]  # which deck has the 3 of clubs
    player_cycler = player_cycler_dict[room] = turn_generator(room, c3_index)
    current_player_dict[room] = next(player_cycler)
    for player_sid, deck in zip(player_sids_dict[room], decks):
        emit('assign cards', {'cards': deck.tolist()}, room=player_sid)
        card_hand_chamber_dict[player_sid] = CardHandChamber(deck)


def turn_generator(room, starting_player_index):
    player_cycle = cycle(player_sids_dict[room])
    # iterates to the current player
    for _ in range(starting_player_index):
        next(player_cycle)
    yield from player_cycle


def next_player(room, round_won=False):
    player_cycler = player_cycler_dict[room]
    current_player = next(player_cycler)
    finished_player_sids = finished_player_sids_dict[room]
    while current_player in finished_player_sids:
        current_player = next(player_cycler)
    current_player_dict[room] = current_player
    name = names_dict[current_player]
    if round_won:
        message_round_won(room, name)
    emit('message', {'msg': f"SERVER: it's {name}'s turn!"}, room=room)


@socketio.on('play current hand', namespace='/presidents')
def maybe_play_current_hand():
    room = get_room()
    name = get_name()
    player_sid = get_sid()
    if player_sid != current_player_dict[room]:
        alert_can_only_play_on_turn()
        return
    hand = get_current_hand(player_sid)
    if not hand.is_valid:
        alert_playing_invalid_hand()
        return
    hand_in_play = hand_in_play_dict[room]
    if hand_in_play is Start:  # hand must contain the 3 of clubs
        if 1 not in hand:
            alert_3_of_clubs()
            return
        else:
            play_hand(hand, room, player_sid, name)
    elif hand_in_play is None:
        play_hand(hand, room, player_sid, name)
    else:
        try:
            if hand > hand_in_play:
                play_hand(hand, room, player_sid, name)
            else:
                alert_weaker_hand()
        except RuntimeError as e:
            emit('alert', {'alert': str(e)}, broadcast=False)


def play_hand(hand: Hand, room: str, player_sid: str, name: str):
    hand_copy = Hand.copy(hand)
    hand_in_play_dict[room] = hand_copy
    client_update_hand_in_play(hand_copy, room)
    message_hand_played(hand_copy, room, name)
    card_hand_chamber = get_card_hand_chamber(player_sid)
    client_clear_current_hand(player_sid)
    # TODO: put this in a function called server clear current hand or something
    for card in hand_copy:
        card_hand_chamber.remove_card(card)
    consecutive_passes_dict[room] = 0
    next_player(room)


def client_update_hand_in_play(hand, room):
    emit('hand in play', {'hand': str(hand)}, room=room)


@socketio.on('player finish', namespace='/presidents')
def player_finish():
    room = get_room()
    name = get_name()
    player_sid = get_sid()
    finished_player_sids_dict[room].append(player_sid)
    num_unfinished_players = num_unfinished_players_dict[room]
    message_player_finished(room, name, position_dict[num_unfinished_players])
    decrement_unfinished_players(room, name)


def decrement_unfinished_players(room, name):
    num_unfinished_players_dict[room] -= 1
    if num_unfinished_players_dict[room] == 1:
        message_player_finished(room, name, position_dict[1])
        end_game_due_diligence(room)


def end_game_due_diligence(room):
    pass


@socketio.on('card click', namespace='/presidents')
def singles_click(data):
    player_sid = get_sid()
    hand = get_current_hand(player_sid)
    card_hand_chamber = get_card_hand_chamber(player_sid)
    # TODO: should I do the conversion in python or javascript (even possible?)
    card = int(data['card'])
    add_or_remove_card(card, hand, card_hand_chamber)
    client_update_current_hand(hand, player_sid)


@socketio.on('hand click', namespace='/presidents')
def hand_click(data):
    player_sid = get_sid()
    hand = get_current_hand(player_sid)
    card_hand_chamber = get_card_hand_chamber(player_sid)
    cards = data['cards']
    client_clear_current_hand(player_sid)
    for card in cards:
        add_or_remove_card(card, hand, card_hand_chamber)
    client_update_current_hand(hand, player_sid)


def add_or_remove_card(card: int, hand: Hand, card_hand_chamber: CardHandChamber):
    # here, we attempt to add a card that has just been clicked:
    #   if the card is not in the current hand, it is added
    #   else, it is remove
    # particular order is to hopefully minimize exceptions but should be
    # verified empirically TODO
    try:
        hand.add(card)
        card_hand_chamber.select_card(card)
    # TODO: should I just pass the error message through no matter the problem?
    #       what is the point of having these separate errors?
    except DuplicateCardError:
        hand.remove(card)
        card_hand_chamber.deselect_card(card)
    except FullHandError:
        alert_current_hand_full()
        # TODO: why do i need the line below
        # client_update_current_hand(hand)  # TODO: this one doesn't require changing the session
        return
    except Exception as e:
        print("Bug: probably the card hand chamber freaking out.")
        raise e


@socketio.on('clear current hand', namespace='/presidents')
def clear_current_hand():
    player_sid = get_sid()
    client_clear_current_hand(player_sid)
    alert_current_hand_cleared()


def client_clear_current_hand(player_sid):
    hand = current_hand_dict[player_sid]
    if hand.is_empty:
        return
    card_hand_chamber = get_card_hand_chamber(player_sid)
    for card in hand:
        card_hand_chamber.deselect_card(card)
    hand.reset()
    emit('clear current hand', room=player_sid)


@socketio.on('pass current hand', namespace='/presidents')
def pass_current_hand():
    """
    handles passing
    """
    room = get_room()
    name = get_name()
    player_sid = get_sid()
    if player_sid != current_player_dict[room]:
        alert_can_only_pass_on_turn()
        return
    hand_in_play = get_hand_in_play(room)
    if hand_in_play is Start:
        alert_must_play_3_of_clubs()
        return
    if hand_in_play is None:
        alert_can_play_any_hand()
        return
    consecutive_passes_dict[room] += 1
    message_passed(room, name)
    num_unfinished_players = num_unfinished_players_dict[room]
    if consecutive_passes_dict[room] == num_unfinished_players - 1:
        next_player(room, True)
        hand_in_play_dict[room] = None
        client_clear_hand_in_play(room)
        return
    next_player(room)


def client_clear_hand_in_play(room):
    emit('clear hand in play', room=room)


@socketio.on('store', namespace='/presidents')
def store():
    """
    stores currently selected cards in a hand
    """
    player_sid = get_sid()
    hand = Hand.copy(get_current_hand(player_sid))
    if not hand.is_valid:
        alert_invalid_hand_storage()
        return
    elif hand.is_single:
        alert_single_storage()
        return
    card_hand_chamber = get_card_hand_chamber(player_sid)
    if card_hand_chamber.contains_hand(hand):
        alert_hand_already_stored()
        return
    client_clear_current_hand(player_sid)
    card_hand_chamber.add_hand(hand)


@socketio.on('clear stored hands', namespace='/presidents')
def clear_stored_hands():
    player_sid = get_sid()
    card_hand_chamber_dict[player_sid].clear_hands()


@socketio.on('left', namespace='/presidents')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    players.remove(request.sid)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


def client_update_current_hand(hand, player_sid):
    if hand.is_empty:
        clear_display()
        return
    else:
        emit('update current hand', {'hand': str(hand)}, room=player_sid)


def clear_display():
    emit('clear display')


def alert_current_hand_cleared():
    emit('alert', {'alert': 'Current hand cleared.'}, broadcast=False)


def alert_stored_hands_cleared():
    emit('alert', {'alert': 'Stored hands cleared.'}, broadcast=False)


def alert_current_hand_full():
    emit('alert', {'alert': 'You cannot add any more cards to this hand.'}, broadcast=False)


def alert_invalid_hand_storage():
    emit('alert', {'alert': 'You can only store valid hands.'}, broadcast=False)


def alert_single_storage():
    emit('alert', {'alert': 'You cannot store singles; play them directly!'}, broadcast=False)


def alert_playing_invalid_hand():
    emit('alert', {'alert': 'You can only play valid hands.'}, broadcast=False)


def alert_3_of_clubs():
    emit('alert', {'alert': 'The first hand must contain the 3 of clubs.'}, broadcast=False)


def alert_weaker_hand():
    emit('alert', {'alert': 'This hand is weaker than the hand in play.'}, broadcast=False)


def alert_can_only_play_on_turn():
    emit('alert', {'alert': 'You can only play hands on your turn.'}, broadcast=False)


def alert_can_only_pass_on_turn():
    emit('alert', {'alert': 'You can only pass on your turn.'}, broadcast=False)


def alert_can_play_any_hand():
    emit('alert', {'alert': 'You can play any hand!'}, broadcast=False)


def alert_must_play_3_of_clubs():
    emit('alert', {'alert': 'You must play a hand containing the 3 of clubs.'}, broadcast=False)


def alert_hand_already_stored():
    emit('alert', {'alert': 'This hand is already stored.'}, broadcast=False)


def message_hand_played(hand, room, name):
    emit('message', {'msg': f"SERVER: {name} played {str(hand)}!"}, room=room)


def message_passed(room, name):
    emit('message', {'msg': f"SERVER: {name} passed!"}, room=room)


def message_round_won(room, name):
    emit('message', {'msg': f"SERVER: {name} won the round!"}, room=room)


def message_player_finished(room, name, position):
    emit('message', {'msg': f"SERVER: {name} is {position}!"})
