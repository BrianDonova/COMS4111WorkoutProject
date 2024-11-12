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

@bp.route('/search', methods=['GET', 'POST'])
def search():
    db = get_db()
    specializations = ["strength training", "cardio", "yoga", "crossfit", "pilates"]  
    experience_levels = [1, 2, 3]
    count = None

    if request.method == 'POST':
        specialization = request.form.get('specialization')
        experience_level = request.form.get('experience_level')
        
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM Trainer
                WHERE specialization = %s AND experience_level = %s;
            """, (specialization, experience_level))
            result = cursor.fetchone()
            count = result['total'] if result else 0

    return render_template('trainer/search.html', specializations=specializations, experience_levels=experience_levels, count=count)
