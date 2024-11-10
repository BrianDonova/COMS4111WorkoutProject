from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db
from psycopg2.extras import DictCursor
from flaskr.auth import login_required

bp = Blueprint('progress', __name__, url_prefix='/progress')

@bp.route('/')
def index():
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT p.progress_id, p.progress_photos_url, p.weekly_summary, p.created_at, m.name AS member_name, m.member_id
            FROM Progress p
            JOIN Creates c ON p.progress_id = c.progress_id
            JOIN Member m ON c.member_id = m.member_id
            ORDER BY p.created_at DESC;
        """)
        progresses = cursor.fetchall()
    return render_template('progress/index.html', progresses=progresses)
