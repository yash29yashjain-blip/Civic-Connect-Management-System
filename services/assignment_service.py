
from flask import current_app


def assign_complaint(complaint_id, department_id):
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """SELECT e.user_id
               FROM employees e
               WHERE e.department_id=%s AND e.active=TRUE
               ORDER BY (
                   SELECT COUNT(*)
                   FROM complaints c
                   WHERE c.assigned_officer_id=e.user_id
                     AND c.status IN ('Assigned', 'In Progress')
               ) ASC, e.user_id ASC
               LIMIT 1""",
            (department_id,)
        )
        employee = cursor.fetchone()

        if not employee:
            return False

        officer_id = employee["user_id"]
        cursor.execute(
            """UPDATE complaints
               SET assigned_officer_id=%s, department_id=%s,
                   status='Assigned'
               WHERE id=%s AND status IN ('Submitted', 'Assigned')""",
            (officer_id, department_id, complaint_id)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return False

        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
