
from models import query_db, execute_db


def get_employees():
    return query_db(
        """SELECT e.id, e.user_id, e.department_id, e.designation,
                  e.active, u.full_name, u.email, d.name AS department_name
           FROM employees e
           JOIN users u ON u.id=e.user_id
           JOIN departments d ON d.id=e.department_id
           ORDER BY u.full_name"""
    )


def get_employee_by_user(user_id):
    return query_db(
        "SELECT * FROM employees WHERE user_id=%s",
        (user_id,),
        fetchone=True
    )


def create_employee(user_id, department_id, designation):
    return execute_db(
        """INSERT INTO employees (user_id, department_id, designation)
           VALUES (%s, %s, %s)""",
        (user_id, department_id, designation)
    )
