
from flask import Blueprint, render_template, session
from flask import current_app
from routes.auth import role_required

citizen_bp = Blueprint("citizen", __name__, url_prefix="/citizen")


@citizen_bp.route("/dashboard")
@role_required("citizen")
def dashboard():
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """SELECT
                   COUNT(*) AS total,
                   SUM(status='Submitted') AS submitted,
                   SUM(status='In Progress') AS in_progress,
                   SUM(status='Resolved') AS resolved
               FROM complaints WHERE citizen_id=%s""",
            (session["user_id"],)
        )
        stats = cursor.fetchone()

        cursor.execute(
            """SELECT c.*, d.name AS department_name
               FROM complaints c
               LEFT JOIN departments d ON d.id=c.department_id
               WHERE c.citizen_id=%s
               ORDER BY c.created_at DESC LIMIT 5""",
            (session["user_id"],)
        )
        recent_complaints = cursor.fetchall()
    finally:
        cursor.close()

    return render_template(
        "citizen/dashboard.html",
        stats=stats,
        complaints=recent_complaints
    )


@citizen_bp.route("/complaints")
@role_required("citizen")
def my_complaints():
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """SELECT c.*, d.name AS department_name
               FROM complaints c
               LEFT JOIN departments d ON d.id=c.department_id
               WHERE c.citizen_id=%s
               ORDER BY c.created_at DESC""",
            (session["user_id"],)
        )
        complaints = cursor.fetchall()
    finally:
        cursor.close()

    return render_template(
        "citizen/my_complaints.html",
        complaints=complaints
    )
