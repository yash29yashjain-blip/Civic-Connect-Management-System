
from models import query_db, execute_db


def get_citizen(user_id):
    return query_db(
        """SELECT id, full_name, email, phone, address, created_at
           FROM users WHERE id=%s AND role='citizen'""",
        (user_id,),
        fetchone=True
    )


def get_citizen_complaints(user_id):
    return query_db(
        """SELECT c.*, d.name AS department_name
           FROM complaints c
           LEFT JOIN departments d ON d.id=c.department_id
           WHERE c.citizen_id=%s
           ORDER BY c.created_at DESC""",
        (user_id,)
    )


def update_citizen(user_id, phone, address):
    return execute_db(
        "UPDATE users SET phone=%s, address=%s "
        "WHERE id=%s AND role='citizen'",
        (phone, address, user_id)
    )
