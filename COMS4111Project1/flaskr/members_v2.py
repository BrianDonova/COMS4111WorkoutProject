from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('members', __name__, url_prefix='/members')

@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Member;")
    members = cursor.fetchall()
    cursor.close()
    return render_template('members/index.html', members=members)

@bp.route('/<int:member_id>')
def detail(member_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Member WHERE member_id = %s;", (member_id,))
    member = cursor.fetchone()
    cursor.close()
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

@bp.route('/search', methods=['GET'])
def search():
    gender = request.args.get('gender')
    
    if not gender:
        flash("Please select a gender to search for.", "error")
        return redirect(url_for('members.index'))
    
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT * FROM Member WHERE gender = %s;
        """, (gender,))
        members = cursor.fetchall()
    
    if not members:
        flash(f"No members found for gender: {gender}", "info")
    
    return render_template('members/search_results.html', members=members, gender=gender)
