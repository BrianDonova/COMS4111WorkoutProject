from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db
from psycopg2.extras import DictCursor
from flaskr.auth import login_required

bp = Blueprint('exercise', __name__, url_prefix='/exercise')

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            # Use ILIKE for case-insensitive search
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
        # Get exercise details and associated workout
        cursor.execute("""
            SELECT e.exercise_id, e.name, e.reps, e.sets, w.name AS workout_name
            FROM Exercises e
            JOIN Contains con ON e.exercise_id = con.exercise_id
            JOIN Workout w ON con.workout_id = w.workout_id
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
