import psycopg2
from flask import current_app, g
import click
from datetime import datetime
from psycopg2.extras import DictCursor  # Import DictCursor


def get_db():
    """Establishes a new database connection if there isn’t one yet for the current application context."""
    if 'db' not in g:
        g.db = psycopg2.connect(
            dbname="w4111",  
            user="bcd2136",  
            password="bcd2136",  
            host="w4111.cisxo09blonu.us-east-1.rds.amazonaws.com",  
            port="5432",
            cursor_factory=DictCursor 
        )
        g.db.autocommit = True 
    
    return g.db


def close_db(e=None):
    """Closes the database connection if it exists."""
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Initializes the database by running the schema.sql file."""
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        with db.cursor() as cursor:
            cursor.execute(f.read())


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Registers the database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
