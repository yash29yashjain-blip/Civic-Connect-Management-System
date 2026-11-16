
from models import query_db, execute_db


def get_departments():
    return query_db("SELECT * FROM departments ORDER BY name")


def get_department(department_id):
    return query_db(
        "SELECT * FROM departments WHERE id=%s",
        (department_id,),
        fetchone=True
    )


def create_department(name, description):
    return execute_db(
        "INSERT INTO departments (name, description) VALUES (%s, %s)",
        (name, description)
    )


def delete_department(department_id):
    return execute_db(
        "DELETE FROM departments WHERE id=%s",
        (department_id,)
    )
