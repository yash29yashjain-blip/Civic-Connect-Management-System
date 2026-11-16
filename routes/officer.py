
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, current_app
)
from routes.auth import role_required

officer_bp = Blueprint("officer", __name__, url_prefix="/officer")

VALID_STATUSES = {
    "Assigned",
    "In Progress",
    "Resolved",
    "Rejected",
}


@officer_bp.route("/dashboard")
@role_required("officer")
def dashboard():
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(status = 'Assigned'), 0) AS assigned,
                COALESCE(SUM(status = 'In Progress'), 0) AS in_progress,
                COALESCE(SUM(status = 'Resolved'), 0) AS resolved
            FROM complaints
            WHERE assigned_officer_id = %s
            """,
            (session["user_id"],)
        )
        stats = cursor.fetchone()

        cursor.execute(
            """
            SELECT c.id, c.title, c.priority, c.status, c.created_at,
                   u.full_name AS citizen_name,
                   d.name AS department_name
            FROM complaints c
            JOIN users u ON u.id = c.citizen_id
            LEFT JOIN departments d ON d.id = c.department_id
            WHERE c.assigned_officer_id = %s
            ORDER BY c.updated_at DESC
            LIMIT 10
            """,
            (session["user_id"],)
        )
        complaints = cursor.fetchall()

    finally:
        cursor.close()

    return render_template(
        "officer/dashboard.html",
        stats=stats,
        complaints=complaints
    )


@officer_bp.route("/complaints", methods=["GET", "POST"])
@role_required("officer")
def manage_complaints():
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    if request.method == "POST":
        complaint_id = request.form.get("complaint_id", "").strip()
        status = request.form.get("status", "").strip()
        notes = request.form.get("officer_notes", "").strip()

        try:
            complaint_id = int(complaint_id)
        except ValueError:
            cursor.close()
            flash("Invalid complaint ID.", "danger")
            return redirect(url_for("officer.manage_complaints"))

        if status not in VALID_STATUSES:
            cursor.close()
            flash("Please select a valid status.", "danger")
            return redirect(url_for("officer.manage_complaints"))

        try:
            cursor.execute(
                """
                UPDATE complaints
                SET status = %s, officer_notes = %s
                WHERE id = %s AND assigned_officer_id = %s
                """,
                (status, notes, complaint_id, session["user_id"])
            )

            if cursor.rowcount == 0:
                connection.rollback()
                flash(
                    "Complaint not found or not assigned to your account.",
                    "danger"
                )
            else:
                connection.commit()
                flash("Complaint status updated successfully.", "success")

        except Exception:
            connection.rollback()
            current_app.logger.exception("Complaint status update failed")
            flash("Could not update the complaint. Please try again.", "danger")

        finally:
            cursor.close()

        return redirect(url_for("officer.manage_complaints"))

    try:
        cursor.execute(
            """
            SELECT c.id, c.title, c.description, c.category,
                   c.location, c.priority, c.status, c.officer_notes,
                   c.created_at, c.updated_at,
                   u.full_name AS citizen_name,
                   d.name AS department_name
            FROM complaints c
            JOIN users u ON u.id = c.citizen_id
            LEFT JOIN departments d ON d.id = c.department_id
            WHERE c.assigned_officer_id = %s
            ORDER BY
                CASE c.priority
                    WHEN 'Urgent' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    ELSE 4
                END,
                c.created_at ASC
            """,
            (session["user_id"],)
        )
        complaints = cursor.fetchall()
    finally:
        cursor.close()

    return render_template(
        "officer/manage_complaints.html",
        complaints=complaints
    )
