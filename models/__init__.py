
from flask import current_app


def query_db(sql, params=(), fetchone=False):
    """Execute a parameterized SELECT query."""
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(sql, params)
        result = cursor.fetchone() if fetchone else cursor.fetchall()
        return result
    finally:
        cursor.close()


def execute_db(sql, params=()):
    """Execute INSERT, UPDATE, or DELETE and commit changes."""
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(sql, params)
        connection.commit()
        return cursor.lastrowid, cursor.rowcount
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
