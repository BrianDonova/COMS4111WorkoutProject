from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from .db import get_db
from psycopg2.extras import DictCursor
from flaskr.auth import login_required

bp = Blueprint('members', __name__, url_prefix='/members')

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            cursor.execute("""
                SELECT member_id, name, email_address, age, gender, height, weight
                FROM Member
                WHERE name ILIKE %s
                ORDER BY name;
            """, (f'%{search_query}%',))
        else:
            cursor.execute("""
                SELECT member_id, name, email_address, age, gender, height, weight
                FROM Member
                ORDER BY name;
            """)
        members = cursor.fetchall()
    return render_template('members/index.html', members=members, search_query=search_query)

@bp.route('/<int:member_id>')
def detail(member_id):
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT member_id, name, email_address, age, gender, height, weight
            FROM Member
            WHERE member_id = %s;
        """, (member_id,))
        member = cursor.fetchone()
    if member is None:
        return "Member not found", 404
    return render_template('members/detail.html', member=member)

@bp.route('/<int:id>/view')
def view(id):
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT member_id, name, email_address, age, gender, height, weight
            FROM Member
            WHERE member_id = %s;
        """, (id,))
        member = cursor.fetchone()

        cursor.execute("""
            SELECT t.trainer_id, t.experience_level, t.certifications, t.specialization
            FROM Trainer t
            JOIN Coaches c ON t.trainer_id = c.trainer_id
            WHERE c.member_id = %s;
        """, (id,))
        trainer = cursor.fetchone()

    return render_template('members/view.html', member=member, trainer=trainer)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        email_address = request.form['email_address']
        age = request.form['age']
        gender = request.form['gender']
        height = request.form['height'] or None
        weight = request.form['weight'] or None
        trainer_id = request.form.get('trainer_id') or None

        error = None

        if not name:
            error = 'Name is required.'
        elif not email_address:
            error = 'Email address is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            try:
                with db.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute("""
                        INSERT INTO Member (name, email_address, age, gender, height, weight)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING member_id;
                    """, (name, email_address, age, gender, height, weight))
                    member_id = cursor.fetchone()['member_id']

                    if trainer_id:
                        cursor.execute("SELECT trainer_id FROM Trainer WHERE trainer_id = %s;", (trainer_id,))
                        trainer = cursor.fetchone()
                        if trainer:
                            cursor.execute("""
                                INSERT INTO Coaches (trainer_id, member_id)
                                VALUES (%s, %s);
                            """, (trainer_id, member_id))
                        else:
                            flash('Trainer ID does not exist. Member created without a trainer.', 'warning')
            except Exception as e:
                db.rollback()
                flash(f'Error: {str(e)}', 'error')
            else:
                db.commit()
                flash('Member created successfully!', 'success')
                return redirect(url_for('members.index'))
    return render_template('members/create.html')



@bp.route('/<int:member_id>/delete', methods=('POST',))
def delete(member_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Coaches WHERE member_id = %s;", (member_id,))
            cursor.execute("DELETE FROM Tracks WHERE member_id = %s;", (member_id,))
            cursor.execute("DELETE FROM Completes WHERE member_id = %s;", (member_id,))
            cursor.execute("DELETE FROM Creates WHERE member_id = %s;", (member_id,))
            cursor.execute("DELETE FROM Member WHERE member_id = %s;", (member_id,))
        db.commit()
        flash('Member deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    return redirect(url_for('members.index'))
