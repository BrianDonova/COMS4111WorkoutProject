from flask import Blueprint, render_template, request
from .db import get_db
from psycopg2.extras import DictCursor

bp = Blueprint('location', __name__, url_prefix='/location')

@bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    db = get_db()
    with db.cursor(cursor_factory=DictCursor) as cursor:
        if search_query:
            cursor.execute("""
                SELECT location_id, amenities, capacity
                FROM Location
                WHERE amenities ILIKE %s
                ORDER BY location_id;
            """, (f'%{search_query}%',))
        else:
            cursor.execute("""
                SELECT location_id, amenities, capacity
                FROM Location
                ORDER BY location_id;
            """)
        locations = cursor.fetchall()
    return render_template('location/index.html', locations=locations, search_query=search_query)
