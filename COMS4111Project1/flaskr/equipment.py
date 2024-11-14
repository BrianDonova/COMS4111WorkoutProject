from flask import Blueprint, render_template, request
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('equipment', __name__, url_prefix='/equipment')

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            # Use ILIKE for case-insensitive search
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
