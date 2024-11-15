from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('equipment', __name__, url_prefix='/equipment')

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            cursor.execute("""
                SELECT equipment_id, name, type
                FROM Equipment
                WHERE name ILIKE %s OR type ILIKE %s
                ORDER BY equipment_id;
            """, (f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute("""
                SELECT equipment_id, name, type
                FROM Equipment
                ORDER BY equipment_id;
            """)
        equipment = cursor.fetchall()
    return render_template('equipment/index.html', equipment=equipment)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        equipment_type = request.form['type']

        if not name or not equipment_type:
            flash('Both name and type are required.', 'error')
            return redirect(url_for('equipment.create'))

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Equipment (name, type)
                    VALUES (%s, %s);
                """, (name, equipment_type))
                db.commit()
                flash('Equipment added successfully!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error adding equipment: {e}', 'error')
            return redirect(url_for('equipment.create'))

        return redirect(url_for('equipment.index'))
    
    return render_template('equipment/create.html')

@bp.route('/<int:equipment_id>/delete', methods=('POST',))
def delete(equipment_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Equipment WHERE equipment_id = %s;", (equipment_id,))
        db.commit()
        flash('Equipment deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting equipment: {e}', 'error')

    return redirect(url_for('equipment.index'))
