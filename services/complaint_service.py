
from flask import current_app

VALID_STATUSES = {
    "Submitted", "Assigned", "In Progress", "Resolved", "Rejected"
}


def change_complaint_status(complaint_id, new_status, notes=""):
    if new_status not in VALID_STATUSES:
        raise ValueError("Invalid complaint status.")

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """UPDATE complaints
               SET status=%s, officer_notes=%s
               WHERE id=%s""",
            (new_status, notes.strip(), complaint_id)
        )
        changed = cursor.rowcount > 0
        connection.commit()
        return changed
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def get_complaint_summary():
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """SELECT status, COUNT(*) AS count
               FROM complaints GROUP BY status"""
        )
        return cursor.fetchall()
    finally:
        cursor.close()
