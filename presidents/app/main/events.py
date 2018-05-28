from hand import Hand, DuplicateCardError, FullHandError
from hand_list import HandList
from flask import session, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio

# TODO: get rid of all the ".get"s
# TODO: figure out how the imports are working lol
# TODO: how to organize helper functions--maybe a different file entirely?
# TODO: move client updates up as early as possible
# TODO: change hand list in session to "stored hands"
# TODO: generally clean the fuck out of this plz wow


@socketio.on('text', namespace='/presidents')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)


@socketio.on('joined', namespace='/presidents')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session['room']
    join_room(room)
    # the first argument of the emit corresponds to the first arg in a 
    # socket.on(...) in the template; basically all this emit is doing
    # is call the function within the socket.on which take in a para-
    # meter 'data' with a dict as the value for 'data'
    emit('status', {'msg': session['name'] + ' has entered the room.'}, room=room)


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


@socketio.on('pass', namespace='/presidents')
def on_pass(data):
    """
    handles passing
    """
    ...


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
    for stored_hand in hand_list:
        if hand.intersects(stored_hand):
            hand_list.remove(stored_hand)
    update_hand_list(hand_list)


def alert_current_hand_cleared():
    emit('alert', {'alert': 'Current hand cleared.'}, broadcast=False)


def alert_current_hand_full():
    emit('alert', {'alert': 'You cannot add any more cards to this hand.'}, broadcast=False)


def alert_invalid_hand_storage():
    emit('alert', {'alert': 'You can only store valid hands.'}, broadcast=False)


def alert_single_storage():
    emit('alert', {'alert': 'You cannot store singles; play them directly!'}, broadcast=False)


def get_current_hand():
    return Hand.from_json(session['hand'])


def update_session_hand(hand):
    session['hand'] = hand.to_json()


def clear_display():
    emit('clear display')
