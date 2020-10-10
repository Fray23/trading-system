import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from database.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).one_or_none()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(name=username).one_or_none()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('admin.setting_view'))
        flash('error')

    return render_template('auth.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
