from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from flaskr.db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('workout', __name__)

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            cursor.execute("""
                SELECT workout_id, name, duration, difficulty_level
                FROM Workout
                WHERE name ILIKE %s
                ORDER BY workout_id;
            """, (f'%{search_query}%',))
        else:
            cursor.execute("""
                SELECT workout_id, name, duration, difficulty_level
                FROM Workout
                ORDER BY workout_id;
            """)
        workouts = cursor.fetchall()
    return render_template('workout/index.html', workouts=workouts, search_query=search_query)

@bp.route('/<int:id>/view')
def view(id):
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        # Fetch workout details
        cursor.execute("""
            SELECT w.workout_id, w.name, w.duration, w.difficulty_level
            FROM Workout w
            WHERE w.workout_id = %s;
        """, (id,))
        workout = cursor.fetchone()

        # Fetch exercises associated with the workout
        cursor.execute("""
            SELECT e.exercise_id, e.name, e.reps, e.sets, e.duration
            FROM Exercises e
            WHERE e.workout_id = %s;
        """, (id,))
        exercises = cursor.fetchall()

        # Fetch members who completed the workout
        cursor.execute("""
            SELECT m.name AS member_name, m.email_address
            FROM Completes c
            JOIN Member m ON c.member_id = m.member_id
            WHERE c.workout_id = %s;
        """, (id,))
        members_completed = cursor.fetchall()

    return render_template('workout/view.html', workout=workout, exercises=exercises, members_completed=members_completed)


@bp.route('/create', methods=('GET', 'POST'))
def create():  # Removed `@login_required` decorator
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
            with db.cursor() as cursor:
                # Insert the new workout
                cursor.execute(
                    '''
                    INSERT INTO Workout (name, duration, difficulty_level)
                    VALUES (%s, %s, %s)
                    RETURNING workout_id;
                    ''',
                    (name, duration, difficulty_level)
                )
                db.commit()
                flash('Workout created successfully!', 'success')
            return redirect(url_for('workout.index'))

    return render_template('workout/create.html')




def get_workout(id, check_author=True):
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(
            '''
            SELECT w.workout_id, w.name, w.duration, w.difficulty_level, c.member_id
            FROM Workout w
            JOIN Completes c ON w.workout_id = c.workout_id
            WHERE w.workout_id = %s;
            ''',
            (id,)
        )
        workout = cursor.fetchone()

    if workout is None:
        abort(404, f"Workout id {id} doesn't exist.")

    if check_author and workout['member_id'] != g.user['member_id']:
        abort(403)

    return workout


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
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
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                    UPDATE Workout
                    SET name = %s, duration = %s, difficulty_level = %s
                    WHERE workout_id = %s;
                    ''',
                    (name, duration, difficulty_level, id)
                )
            db.commit()
            return redirect(url_for('workout.index'))

    return render_template('workout/update.html', workout=workout)


@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            # Delete associated entries from Completes table
            cursor.execute('DELETE FROM Completes WHERE workout_id = %s;', (id,))
            # Delete the workout
            cursor.execute('DELETE FROM Workout WHERE workout_id = %s;', (id,))
        db.commit()
        flash('Workout deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    return redirect(url_for('workout.index'))


