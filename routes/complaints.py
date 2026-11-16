
import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, abort, current_app
)
from werkzeug.utils import secure_filename

from routes.auth import role_required

complaints_bp = Blueprint(
    "complaints",
    __name__,
    url_prefix="/complaints"
)

VALID_PRIORITIES = {"Low", "Medium", "High", "Urgent"}

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_photo(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def find_available_officer(cursor, department_id):
    """Return the user ID of the least-loaded active officer."""

    cursor.execute(
        """
        SELECT
            e.user_id,
            COUNT(c.id) AS active_complaints
        FROM employees e
        LEFT JOIN complaints c
            ON c.assigned_officer_id = e.user_id
            AND c.status NOT IN ('Resolved', 'Rejected')
        WHERE e.department_id = %s
          AND e.active = TRUE
        GROUP BY e.user_id
        ORDER BY active_complaints ASC, e.user_id ASC
        LIMIT 1
        """,
        (department_id,)
    )

    officer = cursor.fetchone()
    return officer["user_id"] if officer else None


@complaints_bp.route("/new", methods=["GET", "POST"])
@role_required("citizen")
def create():
    connection = current_app.extensions["mysql"].connection

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT id, name FROM departments ORDER BY name"
        )
        departments = cursor.fetchall()
    finally:
        cursor.close()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        priority = request.form.get("priority", "Medium").strip()
        department_value = request.form.get("department_id", "").strip()
        photo = request.files.get("photo")

        if not title or not description or not category:
            flash(
                "Title, description, and category are required.",
                "danger"
            )
            return render_template(
                "citizen/create_complaint.html",
                departments=departments
            )

        if priority not in VALID_PRIORITIES:
            flash("Please select a valid priority.", "danger")
            return render_template(
                "citizen/create_complaint.html",
                departments=departments
            )

        # A department is required for automatic officer assignment.
        try:
            department_id = int(department_value)
        except (TypeError, ValueError):
            flash("Please select a valid department.", "danger")
            return render_template(
                "citizen/create_complaint.html",
                departments=departments
            )

        if department_id not in {d["id"] for d in departments}:
            flash("Selected department does not exist.", "danger")
            return render_template(
                "citizen/create_complaint.html",
                departments=departments
            )

        photo_filename = None
        saved_photo_path = None

        # Validate and save an optional photo.
        if photo and photo.filename:
            original_name = secure_filename(photo.filename)

            if not original_name or not allowed_photo(original_name):
                flash(
                    "Upload a JPG, JPEG, PNG, or WEBP image.",
                    "danger"
                )
                return render_template(
                    "citizen/create_complaint.html",
                    departments=departments
                )

            # Generate a unique filename to avoid overwriting other photos.
            extension = original_name.rsplit(".", 1)[1].lower()
            photo_filename = f"{uuid.uuid4().hex}.{extension}"

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "complaints"
            )
            os.makedirs(upload_folder, exist_ok=True)

            saved_photo_path = os.path.join(
                upload_folder,
                photo_filename
            )

            photo.save(saved_photo_path)

            if os.path.getsize(saved_photo_path) > MAX_PHOTO_SIZE:
                os.remove(saved_photo_path)
                flash("Photo size must not exceed 5 MB.", "danger")
                return render_template(
                    "citizen/create_complaint.html",
                    departments=departments
                )

        cursor = connection.cursor()

        try:
            # Assign to the least-loaded active officer in this department.
            assigned_officer_id = find_available_officer(
                cursor,
                department_id
            )

            if assigned_officer_id is not None:
                initial_status = "Assigned"
            else:
                initial_status = "Submitted"

            cursor.execute(
                """
                INSERT INTO complaints (
                    citizen_id,
                    department_id,
                    assigned_officer_id,
                    title,
                    description,
                    category,
                    location,
                    priority,
                    status,
                    photo_filename
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    session["user_id"],
                    department_id,
                    assigned_officer_id,
                    title,
                    description,
                    category,
                    location,
                    priority,
                    initial_status,
                    photo_filename
                )
            )

            connection.commit()

            if assigned_officer_id is not None:
                flash(
                    "Complaint submitted and an officer was assigned automatically.",
                    "success"
                )
            else:
                flash(
                    "Complaint submitted. No active officer is available "
                    "in this department yet.",
                    "warning"
                )

            return redirect(url_for("citizen.my_complaints"))

        except Exception:
            connection.rollback()

            # Remove the uploaded photo if saving the complaint failed.
            if saved_photo_path and os.path.exists(saved_photo_path):
                os.remove(saved_photo_path)

            current_app.logger.exception("Complaint creation failed")
            flash(
                "Could not submit the complaint. Please try again.",
                "danger"
            )

        finally:
            cursor.close()

    return render_template(
        "citizen/create_complaint.html",
        departments=departments
    )


@complaints_bp.route("/<int:complaint_id>")
def detail(complaint_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                c.*,
                citizen.full_name AS citizen_name,
                department.name AS department_name,
                officer.full_name AS officer_name
            FROM complaints c
            JOIN users citizen
                ON citizen.id = c.citizen_id
            LEFT JOIN departments department
                ON department.id = c.department_id
            LEFT JOIN users officer
                ON officer.id = c.assigned_officer_id
            WHERE c.id = %s
            """,
            (complaint_id,)
        )
        complaint = cursor.fetchone()
    finally:
        cursor.close()

    if not complaint:
        abort(404)

    role = session.get("role")
    user_id = session.get("user_id")

    if role == "citizen" and complaint["citizen_id"] != user_id:
        abort(403)

    if (
        role == "officer"
        and complaint["assigned_officer_id"] != user_id
    ):
        abort(403)

    return render_template(
        "citizen/complaint_detail.html",
        complaint=complaint
    )
