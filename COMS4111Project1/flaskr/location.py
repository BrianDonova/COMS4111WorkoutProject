from flask import Blueprint, render_template
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('location', __name__, url_prefix='/location')

@bp.route('/')
def index():
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("""
            SELECT location_id, amenities, capacity
            FROM Location
            ORDER BY location_id;
        """)
        locations = cursor.fetchall()
    return render_template('location/index.html', locations=locations)
