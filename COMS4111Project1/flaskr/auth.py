import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        email_address = request.form['email']
        password = request.form['password']
        age = request.form.get('age')  # Add other fields if needed
        db = get_db()
        error = None

        if not email_address:
            error = 'Email address is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO Member (name, email_address, age, gender, height, weight, password) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (name, email_address, age, 'N/A', 0, 0, generate_password_hash(password))
                    )
                db.commit()
            except psycopg2.IntegrityError:
                error = f"Email {email_address} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email_address = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = None

        with db.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM Member WHERE email_address = %s', (email_address,)
            )
            user = cursor.fetchone()

        if user is None:
            error = 'Incorrect email address.'
        elif not check_password_hash(user[6], password):  # Assuming password is the 7th column
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]  # Assuming member_id is the first column
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    member_id = session.get('user_id')

    if member_id is None:
        g.user = None
    else:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM Member WHERE member_id = %s', (member_id,)
            )
            g.user = cursor.fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view
