from flask import (Blueprint, render_template, session, redirect, url_for,
                   request)
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Required

class LoginForm(FlaskForm):
    """Accepts a nickname and a room."""
    name = StringField('Name', validators=[Required()])
    room = StringField('Room', validators=[Required()])
    submit = SubmitField('Enter Game')

login_blueprint = Blueprint('login_blueprint', __name__)

@login_blueprint.route('/')
def base():
    return redirect(url_for('login_blueprint.login'))

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('login_blueprint.game'))
    return render_template('login/login.html', form=form)

@login_blueprint.route('/game')
def game():
    return redirect(url_for('login_blueprint.login'))
