from flask import Blueprint, render_template, request, redirect, url_for
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
