from flask import Blueprint, render_template, request, redirect, url_for, flash
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
    specializations = ["yoga", "cardio", "strength training", "pilates", "crossfit"]
    experience_levels = [1, 2, 3]  
    count = None

    if request.method == 'POST':
        specialization = request.form.get('specialization')
        experience_level = request.form.get('experience_level')
        
        if specialization not in specializations or experience_level not in experience_levels:
            flash("Invalid entry.", "error")
            return redirect(url_for('trainer.search'))

        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM Trainer
                WHERE specialization = %s AND experience_level = %s;
            """, (specialization, experience_level))
            result = cursor.fetchone()
            count = result['total'] if result else 0

    return render_template('trainer/search.html', specializations=specializations, experience_levels=experience_levels, count=count)

@bp.route('/member_count', methods=['GET', 'POST'])
def member_count():
    db = get_db()
    trainer_id = None
    member_count = None
    experience_level = None

    if request.method == 'POST':
        trainer_id = request.form.get('trainer_id')

        try:
            trainer_id = int(trainer_id)
        except ValueError:
            flash("Trainer ID must be a valid integer.", "error")
            return redirect(url_for('trainer.member_count'))

        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT t.experience_level, COUNT(m.member_id) AS member_count
                FROM Trainer t
                LEFT JOIN Member m ON m.trainer_id = t.trainer_id
                WHERE t.trainer_id = %s
                GROUP BY t.trainer_id;
            """, (trainer_id,))
            result = cursor.fetchone()
            
            if result:
                experience_level = result['experience_level']
                member_count = result['member_count']
            else:
                experience_level = "Trainer not found in directory."
                member_count = 0

    return render_template('trainer/member_count.html', trainer_id=trainer_id, experience_level=experience_level, member_count=member_count)
