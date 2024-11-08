from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from psycopg2.extras import DictCursor


bp = Blueprint('workout', __name__)



@bp.route('/')
def index():
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:  # Use DictCursor here
        cursor.execute(
            'SELECT w.workout_id, w.name, w.duration, w.difficulty_level, m.name AS member_name'
            ' FROM Workout w JOIN Member m ON w.workout_id = m.member_id'
            ' ORDER BY w.name'
        )
        workouts = cursor.fetchall()  # Fetch all results as dictionaries
    
    return render_template('workout/index.html', workouts=workouts)



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        duration = request.form['duration']
        difficulty_level = request.form['difficulty_level']
        error = None

        if not name:
            error = 'Workout name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO Workout (name, duration, difficulty_level, member_id)'
                ' VALUES (?, ?, ?, ?)',
                (name, duration, difficulty_level, g.user['member_id'])
            )
            db.commit()
            return redirect(url_for('workout.index'))

    return render_template('workout/create.html')


def get_workout(id, check_author=True):
    workout = get_db().execute(
        'SELECT w.workout_id, w.name, w.duration, w.difficulty_level, w.member_id'
        ' FROM Workout w JOIN Member m ON w.member_id = m.member_id'
        ' WHERE w.workout_id = ?',
        (id,)
    ).fetchone()

    if workout is None:
        abort(404, f"Workout id {id} doesn't exist.")

    if check_author and workout['member_id'] != g.user['member_id']:
        abort(403)

    return workout

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    workout = get_workout(id)

    if request.method == 'POST':
        name = request.form['name']
        duration = request.form['duration']
        difficulty_level = request.form['difficulty_level']
        error = None

        if not name:
            error = 'Workout name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE Workout SET name = ?, duration = ?, difficulty_level = ?'
                ' WHERE workout_id = ?',
                (name, duration, difficulty_level, id)
            )
            db.commit()
            return redirect(url_for('workout.index'))

    return render_template('workout/update.html', workout=workout)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_workout(id)
    db = get_db()
    db.execute('DELETE FROM Workout WHERE workout_id = ?', (id,))
    db.commit()
    return redirect(url_for('workout.index'))
