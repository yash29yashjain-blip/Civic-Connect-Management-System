
from flask import Blueprint, render_template
from flask import current_app
from routes.auth import role_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@role_required("admin")
def index():
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """SELECT status, COUNT(*) AS total
               FROM complaints GROUP BY status ORDER BY status"""
        )
        status_rows = cursor.fetchall()

        cursor.execute(
            """SELECT d.name AS department_name, COUNT(c.id) AS total
               FROM departments d
               LEFT JOIN complaints c ON c.department_id=d.id
               GROUP BY d.id, d.name ORDER BY total DESC"""
        )
        department_rows = cursor.fetchall()

        cursor.execute(
            """SELECT COUNT(*) AS total,
                      SUM(priority='Urgent') AS urgent,
                      SUM(priority='High') AS high,
                      SUM(status='Resolved') AS resolved
               FROM complaints"""
        )
        summary = cursor.fetchone()
    finally:
        cursor.close()

    return render_template(
        "reports/index.html",
        status_rows=status_rows,
        department_rows=department_rows,
        summary=summary
    )
