from flask import Flask
from flask_socketio import SocketIO
from views.login import login_blueprint 

socketio = SocketIO()
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'yungbanslonely'

app.register_blueprint(login_blueprint)
socketio.init_app(app)

if __name__ == '__main__':
    socketio.run(app)
