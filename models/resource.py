
from models import query_db, execute_db


def get_resources():
    return query_db(
        """SELECT r.*, d.name AS department_name
           FROM resources r
           JOIN departments d ON d.id=r.department_id
           ORDER BY d.name, r.name"""
    )


def create_resource(department_id, name, resource_type, quantity):
    quantity = int(quantity)
    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    return execute_db(
        """INSERT INTO resources
           (department_id, name, resource_type, quantity, available_quantity)
           VALUES (%s, %s, %s, %s, %s)""",
        (department_id, name, resource_type, quantity, quantity)
    )


def update_resource(resource_id, quantity, available_quantity):
    quantity = int(quantity)
    available_quantity = int(available_quantity)

    if quantity < 0 or not 0 <= available_quantity <= quantity:
        raise ValueError("Invalid resource quantities.")

    return execute_db(
        """UPDATE resources
           SET quantity=%s, available_quantity=%s WHERE id=%s""",
        (quantity, available_quantity, resource_id)
    )
