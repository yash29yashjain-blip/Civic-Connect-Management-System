
from models import query_db, execute_db


def get_complaint(complaint_id):
    return query_db(
        """SELECT c.*, u.full_name AS citizen_name,
                  d.name AS department_name
           FROM complaints c
           JOIN users u ON u.id=c.citizen_id
           LEFT JOIN departments d ON d.id=c.department_id
           WHERE c.id=%s""",
        (complaint_id,),
        fetchone=True
    )


def get_all_complaints():
    return query_db(
        """SELECT c.*, u.full_name AS citizen_name,
                  d.name AS department_name
           FROM complaints c
           JOIN users u ON u.id=c.citizen_id
           LEFT JOIN departments d ON d.id=c.department_id
           ORDER BY c.created_at DESC"""
    )


def create_complaint(citizen_id, title, description, category,
                     location, priority, department_id=None):
    return execute_db(
        """INSERT INTO complaints
           (citizen_id, title, description, category, location,
            priority, department_id)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (citizen_id, title, description, category, location,
         priority, department_id)
    )


def update_complaint_status(complaint_id, status, notes=None):
    return execute_db(
        """UPDATE complaints SET status=%s, officer_notes=%s
           WHERE id=%s""",
        (status, notes, complaint_id)
    )
