from hand import Hand

from flask import session, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from .. import socketio



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
    room = session.get('room')
    join_room(room)
    # the first argument of the emit corresponds to the first arg in a 
    # socket.on(...) in the template; basically all this emit is doing
    # is call the function within the socket.on which take in a para-
    # meter 'data' with a dict as the value for 'data'
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)

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
    action = data['action']
    # TODO: should I do the conversion in python or javascript
    card = int(data['card'])
    if action == 'add':
        hand.add(card)
    elif action == 'remove':
        hand.remove(card)
    else:
        raise AssertionError("Bug: unknown action")
    session['hand'] = hand.to_json()
    emit('validity', {'validity': hand.id_desc}, broadcast=False)


@socketio.on('clear hand', namespace='/presidents')
def clear_hand():
    session['hand'] = Hand().to_json()
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