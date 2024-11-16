from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db
from psycopg2.extras import DictCursor
from flaskr.auth import login_required

bp = Blueprint('progress', __name__, url_prefix='/progress')

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            cursor.execute("""
                SELECT p.progress_id, p.progress_photos_url, p.weekly_summary, p.created_at, 
                       m.name AS member_name, m.member_id, 
                       w.workout_id, w.name AS workout_name
                FROM Progress p
                JOIN Creates c ON p.progress_id = c.progress_id
                JOIN Member m ON c.member_id = m.member_id
                LEFT JOIN Stored s ON p.progress_id = s.progress_id
                LEFT JOIN Workout w ON s.workout_id = w.workout_id
                WHERE m.name ILIKE %s OR w.name ILIKE %s
                ORDER BY p.created_at DESC;
            """, (f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("""
                SELECT p.progress_id, p.progress_photos_url, p.weekly_summary, p.created_at, 
                       m.name AS member_name, m.member_id, 
                       w.workout_id, w.name AS workout_name
                FROM Progress p
                JOIN Creates c ON p.progress_id = c.progress_id
                JOIN Member m ON c.member_id = m.member_id
                LEFT JOIN Stored s ON p.progress_id = s.progress_id
                LEFT JOIN Workout w ON s.workout_id = w.workout_id
                ORDER BY p.created_at DESC;
            """)
        progresses = cursor.fetchall()
    return render_template('progress/index.html', progresses=progresses, search_query=search_query)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        member_id = request.form['member_id']
        workout_id = request.form.get('workout_id')
        weekly_summary = request.form['weekly_summary']
        progress_photos_url = request.form['progress_photos_url']
        
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Progress (progress_photos_url, weekly_summary)
                    VALUES (%s, %s)
                    RETURNING progress_id;
                """, (progress_photos_url, weekly_summary))
                progress_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO Creates (member_id, progress_id)
                    VALUES (%s, %s);
                """, (member_id, progress_id))

                if workout_id:
                    cursor.execute("""
                        INSERT INTO Stored (workout_id, progress_id)
                        VALUES (%s, %s);
                    """, (workout_id, progress_id))

                db.commit()
                flash('Progress entry added successfully!', 'success')
                return redirect(url_for('progress.index'))
        except Exception as e:
            db.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('progress.create'))

    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT member_id, name FROM Member ORDER BY name;")
        members = cursor.fetchall()
        cursor.execute("SELECT workout_id, name FROM Workout ORDER BY name;")
        workouts = cursor.fetchall()
    
    return render_template('progress/create.html', members=members, workouts=workouts)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Creates WHERE progress_id = %s;", (id,))
            cursor.execute("DELETE FROM Stored WHERE progress_id = %s;", (id,))
            cursor.execute("DELETE FROM Progress WHERE progress_id = %s;", (id,))
        db.commit()
        flash('Progress entry deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    return redirect(url_for('progress.index'))