from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('exercise', __name__, url_prefix='/exercise')

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            cursor.execute("""
                SELECT e.exercise_id, e.name, e.reps, e.sets, w.name AS workout_name
                FROM Exercises e
                JOIN Workout w ON e.workout_id = w.workout_id
                WHERE e.name ILIKE %s
                ORDER BY e.exercise_id;
            """, (f'%{search_query}%',))
        else:
            cursor.execute("""
                SELECT e.exercise_id, e.name, e.reps, e.sets, w.name AS workout_name
                FROM Exercises e
                JOIN Workout w ON e.workout_id = w.workout_id
                ORDER BY e.exercise_id;
            """)
        exercises = cursor.fetchall()
    return render_template('exercise/index.html', exercises=exercises)

@bp.route('/<int:exercise_id>/view')
def view(exercise_id):
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT e.exercise_id, e.name, e.reps, e.sets, w.name AS workout_name
            FROM Exercises e
            JOIN Workout w ON e.workout_id = w.workout_id
            WHERE e.exercise_id = %s;
        """, (exercise_id,))
        exercise = cursor.fetchone()

        if exercise is None:
            return "Exercise not found.", 404

        cursor.execute("""
            SELECT l.location_id, l.amenities, l.capacity
            FROM Location l
            JOIN Occur o ON l.location_id = o.location_id
            WHERE o.exercise_id = %s;
        """, (exercise_id,))
        locations = cursor.fetchall()
        
        cursor.execute("""
            SELECT eq.equipment_id, eq.name, eq.type
            FROM Equipment eq
            JOIN Requires r ON eq.equipment_id = r.equipment_id
            WHERE r.exercise_id = %s;
        """, (exercise_id,))
        equipment = cursor.fetchall()
        
    return render_template('exercise/view.html', exercise=exercise, locations=locations, equipment=equipment)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        reps = request.form['reps']
        sets = request.form['sets']
        workout_id = request.form['workout_id']

        error = None
        if not name:
            error = 'Exercise name is required.'
        elif not workout_id:
            error = 'Workout ID is required.'

        if error:
            flash(error, 'error')
        else:
            with db.cursor() as cursor:
                try:
                    cursor.execute("""
                        INSERT INTO Exercises (name, reps, sets, workout_id)
                        VALUES (%s, %s, %s, %s);
                    """, (name, reps, sets, workout_id))
                    db.commit()
                    flash('Exercise created successfully!', 'success')
                    return redirect(url_for('exercise.index'))
                except Exception as e:
                    db.rollback()
                    flash(f'An error occurred: {e}', 'error')
    
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT workout_id, name FROM Workout;")
        workouts = cursor.fetchall()
    
    return render_template('exercise/create.html', workouts=workouts)

@bp.route('/<int:exercise_id>/delete', methods=('POST',))
def delete(exercise_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Exercises WHERE exercise_id = %s;", (exercise_id,))
        db.commit()
        flash('Exercise deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'An error occurred: {e}', 'error')
    return redirect(url_for('exercise.index'))
