from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('trainer', __name__, url_prefix='/trainer')

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            cursor.execute("""
                SELECT trainer_id, experience_level, certifications, specialization
                FROM Trainer
                WHERE experience_level::text ILIKE %s
                OR certifications ILIKE %s
                OR specialization ILIKE %s
                ORDER BY trainer_id;
            """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("""
                SELECT trainer_id, experience_level, certifications, specialization
                FROM Trainer
                ORDER BY trainer_id;
            """)
        trainers = cursor.fetchall()
    return render_template('trainer/index.html', trainers=trainers, search_query=search_query)

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


@bp.route('/add', methods=('GET', 'POST'))
def add_trainer():
    if request.method == 'POST':
        experience_level = request.form['experience_level']
        certifications = request.form['certifications']
        specialization = request.form['specialization']

        # Error validation
        error = None
        if not experience_level:
            error = 'Experience level is required.'
        elif not certifications:
            error = 'Certifications are required.'
        elif not specialization:
            error = 'Specialization is required.'

        if error:
            flash(error, 'error')
        else:
            db = get_db()
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO Trainer (experience_level, certifications, specialization)
                        VALUES (%s, %s, %s);
                        """,
                        (experience_level, certifications, specialization)
                    )
                db.commit()
                flash('Trainer added successfully!', 'success')
                return redirect(url_for('trainer.index'))
            except Exception as e:
                db.rollback()
                flash(f'An error occurred: {str(e)}', 'error')

    return render_template('trainer/add.html')



@bp.route('/<int:trainer_id>/delete', methods=('POST',))
def delete_trainer(trainer_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Trainer WHERE trainer_id = %s;", (trainer_id,))
            db.commit()
            flash('Trainer deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    return redirect(url_for('trainer.index'))
