from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('nutrition', __name__, url_prefix='/nutrition')

@bp.route('/')
def index():
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT n.nutrition_id, n.name, n.calories, n.proteins, n.carbohydrates, n.created_at, m.name AS member_name, m.member_id
            FROM Nutrition n
            JOIN Tracks t ON n.nutrition_id = t.nutrition_id
            JOIN Member m ON t.member_id = m.member_id
            ORDER BY n.created_at DESC;
        """)
        nutritions = cursor.fetchall()
    return render_template('nutrition/index.html', nutritions=nutritions)

@bp.route('/add', methods=('GET', 'POST'))
def add_nutrition():
    if request.method == 'POST':
        name = request.form['name']
        calories = request.form['calories']
        proteins = request.form['proteins']
        carbohydrates = request.form['carbohydrates']
        member_name = request.form['member_name']

        db = get_db()
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT member_id FROM Member WHERE name = %s", (member_name,))
            member = cursor.fetchone()
            
            if member is None:
                flash('Error: Member does not exist. Please enter a valid member name.', 'error')
                return redirect(url_for('nutrition.add_nutrition'))

            member_id = member['member_id']
                
            cursor.execute("""
                INSERT INTO Nutrition (name, calories, proteins, carbohydrates)
                VALUES (%s, %s, %s, %s) RETURNING nutrition_id
            """, (name, calories, proteins, carbohydrates))
            nutrition_id = cursor.fetchone()['nutrition_id']

            cursor.execute("INSERT INTO Tracks (member_id, nutrition_id) VALUES (%s, %s)", (member_id, nutrition_id))
            
            db.commit()

        flash('Nutrition information added successfully!', 'success')
        return redirect(url_for('nutrition.index'))

    return render_template('nutrition/add.html')
