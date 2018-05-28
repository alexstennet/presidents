from hand import Hand, DuplicateCardError, FullHandError
from hand_list import HandList
from flask import session, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio

# TODO: get rid of all the ".get"s
# TODO: figure out how the imports are working lol


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
    try:
        hand.add(card)
        emit('select', {'card': card})
    # TODO: should I just pass the error message through no matter the problem?
    #       what is the point of having these separate errors?
    except DuplicateCardError:
        hand.remove(card)
        emit('unselect', {'card': card})
    except FullHandError:
        message_current_hand_full()
        message_hand(hand) # TODO: this one doesn't require changing the session
        return
    except Exception as e:  # TODO: is this even possible?
        print("Bug: unknown action")
        raise e
    session['hand'] = hand.to_json()
    message_hand(hand)


@socketio.on('clear hand', namespace='/presidents')
def clear_hand():
    hand = Hand.from_json(session['hand'])
    if hand.is_empty:
        return
    for card in hand:
        # TODO: this is where the first uint8 bs happens--requires int convert
        emit('unselect', {'card': int(card)}, broadcast=False)
    hand = Hand()
    session['hand'] = hand.to_json()
    message_current_hand_cleared()


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
        message_invalid_hand_storage()
        return
    elif hand.is_single:
        message_single_storage()
        return
    hand_list = get_hand_list()
    if hand in hand_list:
        return
    hand_list.add(hand)
    session['hand_list'] = hand_list.to_json()
    emit('clear hands')
    for hand in hand_list:
        emit('store hand', {'hand': hand.to_json(), 'id_desc': hand.id_desc}, broadcast=False)


def get_hand_list():
    return HandList.from_json(session['hand_list'])


@socketio.on('left', namespace='/presidents')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


# TODO: move special messages to their own folder


def message_hand(hand):
    emit('current hand', {'hand': session['hand'], 'id_desc': hand.id_desc}, broadcast=False)


def message_current_hand_cleared():
    emit('alert', {'alert': 'Current hand cleared.'}, broadcast=False)


def message_current_hand_full():
    emit('alert', {'alert': 'You cannot add any more cards to this hand.'}, broadcast=False)


def message_invalid_hand_storage():
    emit('alert', {'alert': 'You can only store valid hands.'}, broadcast=False)


def message_single_storage():
    emit('alert', {'alert': 'You cannot store singles; play them directly!'}, broadcast=False)


def get_current_hand():
    return Hand.from_json(session['hand'])


def update_session_hand(hand):
    session['hand'] = hand.to_json()


