from flask import Blueprint, render_template
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('equipment', __name__, url_prefix='/equipment')

@bp.route('/')
def index():
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT equipment_id, name, type
            FROM Equipment
            ORDER BY equipment_id;
        """)
        equipment = cursor.fetchall()
    return render_template('equipment/index.html', equipment=equipment)
