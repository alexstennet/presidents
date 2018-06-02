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

# TODO: where to put these
current_hand_dict: Dict[str, Hand] = dict()
# TODO: should not be a dict from sid so another player can take over
card_hand_chamber_dict: Dict[str, CardHandChamber]
hand_in_play_dict: Dict[str, Hand] = dict()
player_sids_dict: Dict[str, List[str]] = dict()
player_cycler_dict: Dict[str, Generator[str, None, None]] = dict()
current_player_dict: Dict[str, str] = dict()
finished_player_sids_dict: Dict[str, List[str]] = dict()
num_finished_players_dict: Dict[str, int] = dict()
consecutive_passes_dict: Dict[str, int] = dict()
names_dict: Dict[str, str] = dict()


def get_room() -> str:
    return session['room']


def get_name() -> str:
    return session['name']


def get_sid() -> str:
    return request.sid


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
    if len(player_sids_dict[room]) == 1:
        start_game(room)


def add_player(room, name, player_sid):
    names_dict[player_sid] = name
    player_sids_dict[room].append(player_sid)
    current_hand_dict[player_sid] = Hand()


# TODO: don't really like this but like wut do
class Start:  # for playing the 3 of clubs on 
    pass
Start = Start()


def start_game(room):
    deal_cards_and_establish_turn_order(room)
    hand_in_play_dict[room] = Start


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


def turn_generator(room, starting_player_index):
    player_cycle = cycle(player_sids_dict[room])
    # iterates to the current player
    for _ in range(starting_player_index):
        next(player_cycle)
    yield from player_cycle


def next_player(room):
    player_cycler = player_cycler_dict[room]
    current_player = next(player_cycler)
    finished_player_sids = finished_player_sids_dict[room]
    while current_player in finished_player_sids:
        current_player = next(player_cycler)
    current_player_dict[room] = current_player
    name = names_dict[room][current_player]
    emit('message', {'msg': f"SERVER: it's {name}'s turn!"}, room=room)


@socketio.on('play current hand', namespace='/presidents')
def play_current_hand():
    room = get_room()
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
            # TODO: clearly need to bundle these together
            hand_in_play_dict[room] = hand
            client_update_hand_in_play(hand)
            clear_current_hand_helper()
            remove_cards_in_hand(hand)
            maybe_remove_stored_hands(hand)
            message_hand_played(hand)
            consecutive_passes = 0
            next_player()
    elif hand_in_play is None:
        last_played[room] = hand
        client_update_hand_in_play(hand)
        clear_current_hand_helper()
        remove_cards_in_hand(hand)
        maybe_remove_stored_hands(hand)
        message_hand_played(hand)
        consecutive_passes = 0
        next_player()
    else:
        try:
            if hand > hand_in_play:
                last_played[room] = hand
                client_update_hand_in_play(hand)
                clear_current_hand_helper()
                remove_cards_in_hand(hand)
                maybe_remove_stored_hands(hand)
                message_hand_played(hand)
                consecutive_passes = 0
                next_player()
            else:
                alert_weaker_hand()
        except RuntimeError as e:
            emit('alert', {'alert': str(e)}, broadcast=False)


def client_update_hand_in_play(hand):
    room = session['room']
    emit('hand in play', {'hand': str(hand)}, room=room)


def remove_cards_in_hand(hand):
    for card in hand:
        # TODO: uint8 error here again
        emit('remove card', {'card': int(card)}, broadcast=False)










@socketio.on('card click', namespace='/presidents')
def singles_click(data):
    player_sid = get_sid()
    hand = get_current_hand(player_sid)
    card_hand_chamber = get_card_hand_chamber(player_sid)
    # TODO: should I do the conversion in python or javascript (even possible?)
    card = int(data['card'])
    add_or_remove_card(card, hand, card_hand_chamber)
    client_update_hand(hand)


@socketio.on('hand click', namespace='/presidents')
def hand_click(data):
    player_sid = get_sid()
    hand = get_current_hand(player_sid)
    card_hand_chamber = get_card_hand_chamber(player_sid)
    cards = data['cards']
    for card in cards:
        add_or_remove_card(card, hand, card_hand_chamber)


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
        # client_update_hand(hand)  # TODO: this one doesn't require changing the session
        return
    except Exception as e:
        print("Bug: probably the card hand chamber freaking out")
        raise e


@socketio.on('clear current hand', namespace='/presidents')
def clear_current_hand():
    # TODO: make this cleaner; specifically identify what each function
    #       is doing and name them accordingly
    clear_current_hand_helper()
    alert_current_hand_cleared()


def clear_current_hand_helper():
    hand = Hand.from_json(session['hand'])
    if hand.is_empty:
        return
    for card in hand:
        client_deselect_card(card)
    hand = Hand()
    maybe_highlight_stored_hands(hand)
    session['hand'] = hand.to_json()
    emit('clear current hand')


@socketio.on('pass current hand', namespace='/presidents')
def pass_current_hand():
    """
    handles passing
    """
    if request.sid != current_player:
        alert_can_only_pass_on_turn()
        return
    lp = get_last_played()
    if lp is Start:
        alert_must_play_3_of_clubs()
        return
    if lp is None:
        alert_can_play_any_hand()
        return
    global consecutive_passes
    consecutive_passes += 1
    message_passed()
    if consecutive_passes == players_remaining - 1:
        message_round_won()
        next_player()
        last_played[session['room']] = None
        emit('clear hand in play', room=session['room'])
        return
    next_player()


@socketio.on('store', namespace='/presidents')
def store():
    """
    stores currently selected cards in a hand
    """
    hand = get_current_hand()
    if not hand.is_valid:
        alert_invalid_hand_storage()
        return
    elif hand.is_single:
        alert_single_storage()
        return
    hand_list = get_hand_list()
    if hand in hand_list:
        return
    hand_list.add(hand)
    session['hand_list'] = hand_list.to_json()
    clear_current_hand_helper()
    emit('clear stored hands')  # this clears all hands from client view for re-adding
    update_hand_list(hand_list)  # TODO: make it more clear that this affects the client view


def update_hand_list(hand_list):  # TODO: is that what this function is doing?
    # TODO: why doesn't this function clear the stored hands first?
    for hand in hand_list:
        store_hand(hand, 'green')


# TODO: o god reaching the point where the naming is getting fucky
def store_hand(hand, color):
    emit('store hand', {'hand': hand.to_json(), 'str': str(hand), 'color': color}, broadcast=False)


@socketio.on('clear stored hands', namespace='/presidents')
def clear_stored_hands():
    session['hand_list'] = HandList().to_json()
    emit('clear stored hands')


def get_hand_list():
    return HandList.from_json(session['hand_list'])


@socketio.on('left', namespace='/presidents')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    players.remove(request.sid)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


def client_select_card(card):
    # TODO: this is where the first uint8 bs happens--requires int convert
    emit('select card', {'card': int(card)}, broadcast=False)


def client_deselect_card(card):
    emit('deselect card', {'card': int(card)}, broadcast=False)


def client_update_hand(hand):
    if hand.is_empty:
        clear_display()
        return
    else:
        emit('current hand', {'hand': str(hand)}, broadcast=False)
    maybe_highlight_stored_hands(hand)


def maybe_highlight_stored_hands(hand):
    hand_list = get_hand_list()
    emit('clear stored hands')
    for stored_hand in hand_list:
        if hand.intersects(stored_hand):
            color = 'red'
        else:
            color = 'green'
        store_hand(stored_hand, color)


def maybe_remove_stored_hands(hand):
    hand_list = get_hand_list()
    hand_list_copy = HandList.copy(hand_list)
    for stored_hand in hand_list_copy:
        if hand.intersects(stored_hand):
            hand_list.remove(stored_hand)
    update_hand_list(hand_list)
    session['hand_list'] = hand_list.to_json()


def get_last_played():
    return last_played.get(session['room'], None)


def alert_current_hand_cleared():
    emit('alert', {'alert': 'Current hand cleared.'}, broadcast=False)


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


def message_hand_played(hand):
    name = session['name']
    room = session['room']
    emit('message', {'msg': f"SERVER: {name} played {str(hand)}!"}, room=room)


def message_passed():
    name = session['name']
    room = session['room']
    emit('message', {'msg': f"SERVER: {name} passed!"}, room=room)


def message_round_won():
    name = session['name']
    room = session['room']
    emit('message', {'msg': f"SERVER: {name} won the round!"}, room=room)


def get_current_hand(player_sid):
    return current_hand_dict[player_sid]


def get_card_hand_chamber(player_sid):
    return card_hand_chamber_dict[player_sid]


def update_session_hand(hand):
    session['hand'] = hand.to_json()


def clear_display():
    emit('clear display')
