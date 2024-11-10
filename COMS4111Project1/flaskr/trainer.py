from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('trainer', __name__, url_prefix='/trainer')

@bp.route('/')
def index():
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT trainer_id, experience_level, certifications, specialization
            FROM Trainer
            ORDER BY trainer_id;
        """)
        trainers = cursor.fetchall()
    return render_template('trainer/index.html', trainers=trainers)
