from flask import Blueprint, render_template, request, redirect, url_for
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
