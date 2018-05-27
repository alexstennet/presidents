from hand import Hand, DuplicateCardError, FullHandError

from flask import session, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio

# TODO: get rid of all the ".get"s

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
def on_singles_click(data):
    """
    handles clicking on selected and unselected singles that belong to
    the respective player

    data contains the spot number and the card clicked on

    should update hand id and whether or not it beats the hand currently
    being played on

    if the hand is valid, allows storage
    """
    hand = Hand.from_json(session['hand'])
    # TODO: should I do the conversion in python or javascript
    card = int(data['card'])
    try:
        hand.add(card)
        emit('select', {'card': card})
    # TODO: should I just pass the error message through no matter the problem?
    except DuplicateCardError:
        hand.remove(card)
        emit('unselect', {'card': card})
    except FullHandError:
        emit('full', broadcast=False)
    except Exception as e:
        print("Bug: unknown action")
        raise e
    session['hand'] = hand.to_json()
    emit('show', {'repr': session['hand']}, broadcast=False)


@socketio.on('clear hand', namespace='/presidents')
def clear_hand():
    hand = Hand.from_json(session['hand'])
    session['hand'] = Hand().to_json()
    for card in hand:
        # TODO: this is where the first uint8 bs happens--requires int convert
        emit('unselect', {'card': int(card)}, broadcast=False)
    emit('cleared', broadcast=False)


@socketio.on('pass', namespace='/presidents')
def on_pass(data):
    """
    handles passing
    """
    ...


@socketio.on('store', namespace='/presidents')
def on_store(data):
    """
    stores currently selected cards in a hand
    """
    ...


@socketio.on('left', namespace='/presidents')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)