from hand import Hand, DuplicateCardError, FullHandError
from hand_list import HandList
from flask import request, session, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from typing import Dict, List
from itertools import cycle
import numpy as np

# TODO: get rid of all the ".get"s
# TODO: figure out how the imports are working lol
# TODO: how to organize helper functions--maybe a different file entirely?
# TODO: move client updates up as early as possible
# TODO: change hand list in session to "stored hands"
# TODO: generally clean the fuck out of this plz wow
# TODO: doing the whole global thing?

# TODO: where to put this and also how to handle hecka rooms?
# TODO: wait does this even have to be a dict lol
# a dict from room to Hand object
last_played: Dict[str, Hand] = dict()

# TODO: alternatives?
players: List[str] = list()
current_player: str = None
player_cycler = None  # TODO: generator type hint
players_remaining = 0
consecutive_passes = 0
names = dict()


# TODO: don't really like this but like wut do
class Start:
    """
    for playing the 3 of clubs on 
    """
    pass
Start: "Start" = Start()


@socketio.on('text', namespace='/presidents')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': f"{session['name']}: {message['msg']}"}, room=room)


@socketio.on('joined', namespace='/presidents')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session['room']
    join_room(room)
    add_players(room)
    # the first argument of the emit corresponds to the first arg in a 
    # socket.on(...) in the template; basically all this emit is doing
    # is call the function within the socket.on which take in a para-
    # meter 'data' with a dict as the value for 'data'
    emit('status', {'msg': session['name'] + ' has entered the room.'}, room=room)
    if len(players) == 4:
        start_game(room)


def ready_to_deal():
    to_deal = np.arange(1, 53)  # to_deal is a list of lists of cards
    np.random.shuffle(to_deal)
    to_deal = to_deal.reshape(4, 13)
    # to_deal = to_deal.reshape(2, 26)  # for 2 player mode
    to_deal.sort(axis=1)
    return to_deal


def start_game(room):
    to_deal = ready_to_deal()
    # to_deal = np.arange(1, 53).reshape(2, 26)  # for debugging
    global player_cycler, current_player, players_remaining
    player_cycler = turn_generator(index_with_3_of_clubs(to_deal))
    current_player = next(player_cycler)
    players_remaining = 4
    deal_cards(to_deal, room)
    last_played[session['room']] = Start


def next_player():
    global current_player
    current_player = next(player_cycler)
    name = names[current_player]
    room = session['room']
    emit('message', {'msg': f"SERVER: it's {name}'s turn!"}, room=room)


def index_with_3_of_clubs(to_deal):  # to_deal is a list of lists of cards
    return np.where(to_deal == 1)[0][0]  # TODO: justify/benchmark


# TODO: where/how to handle starting card having to include 3 of clubs 
@socketio.on('play current hand', namespace='/presidents')
def play_current_hand():
    global consecutive_passes
    if request.sid != current_player:
        alert_can_only_play_on_turn()
        return
    hand = get_current_hand()
    if not hand.is_valid:
        alert_playing_invalid_hand()
        return
    room = session['room']
    hand_in_play = last_played.get(room, None)
    if hand_in_play is Start:  # hand must contain the 3 of clubs
        if 1 not in hand:
            alert_3_of_clubs()
            return
        else:
            # TODO: clearly need to bundle these together
            last_played[room] = hand
            update_hand_in_play(hand)
            clear_current_hand_helper()
            remove_cards_in_hand(hand)
            maybe_remove_stored_hands(hand)
            message_hand_played(hand)
            consecutive_passes = 0
            next_player()
    elif hand_in_play is None:
        last_played[room] = hand
        update_hand_in_play(hand)
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
                update_hand_in_play(hand)
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


def update_hand_in_play(hand):
    room = session['room']
    emit('hand in play', {'hand': str(hand)}, room=room)


def remove_cards_in_hand(hand):
    for card in hand:
        # TODO: uint8 error here again
        emit('remove card', {'card': int(card)}, broadcast=False)


def deal_cards(to_deal, room):
    for player, cards in zip(players, to_deal):
        emit('assign cards', {'cards': cards.tolist()}, room=player)


def add_players(room):
    names[request.sid] = session['name']
    players.append(request.sid)


def turn_generator(starting_player_index):
    """
    should be recalled everytime a player is finished
    """
    player_cycle = cycle(players)
    # iterates to the current player
    for _ in range(starting_player_index):
        next(player_cycle)
    yield from player_cycle


@socketio.on('singles click', namespace='/presidents')
def singles_click(data):
    """
    handles clicking on selected and unselected singles that belong to
    the respective player

    data contains the spot number and the card clicked on

    should update hand id and whether or not it beats the hand currently
    being played on

    if the hand is valid, allows storage
    """
    hand = Hand.from_json(session['hand'])
    # TODO: should I do the conversion in python or javascript (even possible?)
    card = int(data['card'])
    # here, we attempt to add a card that has just been clicked:
    #   if the card is not in the current hand, it is added
    #   else, it is remove
    # particular order is to hopefully minimize exceptions but should be
    # verified empirically TODO
    try:
        hand.add(card)
        select_card(card)
    # TODO: should I just pass the error message through no matter the problem?
    #       what is the point of having these separate errors?
    except DuplicateCardError:
        hand.remove(card)
        deselect_card(card)
    except FullHandError:
        alert_current_hand_full()
        update_hand_id(hand)  # TODO: this one doesn't require changing the session
        return
    except Exception as e:  # TODO: is this even possible?
        print("Bug: unknown action")
        raise e
    update_hand_id(hand)
    maybe_highlight_stored_hands(hand)
    session['hand'] = hand.to_json()


@socketio.on('hand click', namespace='/presidents')
def hand_click(data):
    hand = Hand.from_json(data['hand'])
    clear_current_hand_helper()  # TODO: again, do not like plz
    update_hand_id(hand)
    for card in hand:
        select_card(card)
    maybe_highlight_stored_hands(hand)
    session['hand'] = hand.to_json()


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
        deselect_card(card)
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


def select_card(card):
    # TODO: this is where the first uint8 bs happens--requires int convert
    emit('select card', {'card': int(card)}, broadcast=False)


def deselect_card(card):
    emit('deselect card', {'card': int(card)}, broadcast=False)


def update_hand_id(hand):
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


def get_current_hand():
    return Hand.from_json(session['hand'])


def update_session_hand(hand):
    session['hand'] = hand.to_json()


def clear_display():
    emit('clear display')
