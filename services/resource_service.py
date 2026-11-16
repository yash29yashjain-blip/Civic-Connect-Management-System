
from flask import current_app


def allocate_resource(resource_id, amount):
    """Reserve a quantity of a resource if enough units are available."""
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a whole number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """UPDATE resources
               SET available_quantity=available_quantity-%s
               WHERE id=%s AND available_quantity >= %s""",
            (amount, resource_id, amount)
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


def release_resource(resource_id, amount):
    """Return reserved units without exceeding total quantity."""
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a whole number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """UPDATE resources
               SET available_quantity=available_quantity+%s
               WHERE id=%s
                 AND available_quantity+%s <= quantity""",
            (amount, resource_id, amount)
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
