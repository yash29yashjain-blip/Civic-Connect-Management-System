
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app
)
from werkzeug.security import generate_password_hash
from routes.auth import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        users = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM complaints")
        complaints = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM complaints "
            "WHERE status = 'Submitted'"
        )
        submitted = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM complaints "
            "WHERE status = 'Resolved'"
        )
        resolved = cursor.fetchone()["total"]

        stats = {
            "users": users,
            "complaints": complaints,
            "submitted": submitted,
            "resolved": resolved
        }

    finally:
        cursor.close()

    return render_template(
        "admin/dashboard.html",
        stats=stats
    )


# ==========================================
# DEPARTMENT MANAGEMENT
# ==========================================

@admin_bp.route("/departments", methods=["GET", "POST"])
@role_required("admin")
def departments():
    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            cursor.close()
            flash("Please enter a department name.", "danger")
            return redirect(url_for("admin.departments"))

        try:
            cursor.execute(
                """
                INSERT INTO departments (name, description)
                VALUES (%s, %s)
                """,
                (name, description)
            )

            connection.commit()

            flash(
                "Department added successfully!",
                "success"
            )

        except Exception:
            connection.rollback()
            current_app.logger.exception(
                "Department creation failed"
            )

            flash(
                "Could not add department. "
                "The department may already exist.",
                "danger"
            )

        finally:
            cursor.close()

        return redirect(url_for("admin.departments"))

    try:
        cursor.execute(
            "SELECT * FROM departments ORDER BY name"
        )

        department_list = cursor.fetchall()

    finally:
        cursor.close()

    return render_template(
        "admin/departments.html",
        departments=department_list
    )


# ==========================================
# DELETE DEPARTMENT
# ==========================================

@admin_bp.route(
    "/departments/delete/<int:department_id>",
    methods=["POST"]
)
@role_required("admin")
def delete_department(department_id):

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        # Check whether department exists
        cursor.execute(
            "SELECT id FROM departments WHERE id = %s",
            (department_id,)
        )

        department = cursor.fetchone()

        if not department:
            flash("Department not found.", "danger")
            return redirect(url_for("admin.departments"))

        # Check linked employees
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM employees
            WHERE department_id = %s
            """,
            (department_id,)
        )

        employee_count = cursor.fetchone()["total"]

        # Check linked resources
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM resources
            WHERE department_id = %s
            """,
            (department_id,)
        )

        resource_count = cursor.fetchone()["total"]

        # Check linked complaints
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM complaints
            WHERE department_id = %s
            """,
            (department_id,)
        )

        complaint_count = cursor.fetchone()["total"]

        if employee_count or resource_count or complaint_count:

            flash(
                "Cannot delete this department because it is linked "
                "to employees, resources, or complaints.",
                "warning"
            )

        else:
            cursor.execute(
                "DELETE FROM departments WHERE id = %s",
                (department_id,)
            )

            connection.commit()

            flash(
                "Department deleted successfully!",
                "success"
            )

    except Exception:
        connection.rollback()

        current_app.logger.exception(
            "Department deletion failed"
        )

        flash(
            "Could not delete department.",
            "danger"
        )

    finally:
        cursor.close()

    return redirect(url_for("admin.departments"))


# ==========================================
# EMPLOYEE / OFFICER MANAGEMENT
# ==========================================

@admin_bp.route("/employees", methods=["GET", "POST"])
@role_required("admin")
def employees():

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    if request.method == "POST":

        full_name = request.form.get(
            "full_name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get("password", "")

        designation = request.form.get(
            "designation",
            "Public Service Officer"
        ).strip()

        department_value = request.form.get(
            "department_id", ""
        ).strip()

        try:
            department_id = int(department_value)

        except ValueError:
            cursor.close()

            flash(
                "Please select a valid department.",
                "danger"
            )

            return redirect(url_for("admin.employees"))

        if not full_name or not email or len(password) < 8:

            cursor.close()

            flash(
                "Enter a name, valid email, and password "
                "of at least 8 characters.",
                "danger"
            )

            return redirect(url_for("admin.employees"))

        try:
            # Check department
            cursor.execute(
                "SELECT id FROM departments WHERE id = %s",
                (department_id,)
            )

            if not cursor.fetchone():

                flash(
                    "The selected department does not exist.",
                    "danger"
                )

                return redirect(url_for("admin.employees"))

            # Check duplicate email
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            if cursor.fetchone():

                flash(
                    "That email address is already registered.",
                    "danger"
                )

                return redirect(url_for("admin.employees"))

            # Create officer user
            cursor.execute(
                """
                INSERT INTO users
                    (full_name, email, password_hash, role)
                VALUES (%s, %s, %s, 'officer')
                """,
                (
                    full_name,
                    email,
                    generate_password_hash(password)
                )
            )

            user_id = cursor.lastrowid

            # Create employee record
            cursor.execute(
                """
                INSERT INTO employees
                    (user_id, department_id, designation, active)
                VALUES (%s, %s, %s, TRUE)
                """,
                (
                    user_id,
                    department_id,
                    designation or "Public Service Officer"
                )
            )

            connection.commit()

            flash(
                "Officer account created successfully!",
                "success"
            )

            return redirect(url_for("admin.employees"))

        except Exception:
            connection.rollback()

            current_app.logger.exception(
                "Officer creation failed"
            )

            flash(
                "Could not create officer account. "
                "Check the application log.",
                "danger"
            )

            return redirect(url_for("admin.employees"))

        finally:
            cursor.close()

    try:
        # Fetch departments
        cursor.execute(
            "SELECT id, name FROM departments ORDER BY name"
        )

        department_list = cursor.fetchall()

        # Fetch officers
        cursor.execute(
            """
            SELECT
                u.id,
                u.full_name,
                u.email,
                e.designation,
                e.active,
                d.name AS department_name
            FROM employees e
            JOIN users u
                ON u.id = e.user_id
            JOIN departments d
                ON d.id = e.department_id
            WHERE u.role = 'officer'
            ORDER BY u.full_name
            """
        )

        employee_list = cursor.fetchall()

    finally:
        cursor.close()

    return render_template(
        "admin/employees.html",
        departments=department_list,
        employees=employee_list
    )


# ==========================================
# RESOURCE MANAGEMENT
# ==========================================

@admin_bp.route("/resources", methods=["GET", "POST"])
@role_required("admin")
def resources():

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    if request.method == "POST":

        department_value = request.form.get(
            "department_id", ""
        ).strip()

        name = request.form.get(
            "name", ""
        ).strip()

        resource_type = request.form.get(
            "resource_type", ""
        ).strip()

        quantity_value = request.form.get(
            "quantity", ""
        ).strip()

        try:
            department_id = int(department_value)
            quantity = int(quantity_value)

            if not name or not resource_type:
                raise ValueError("Missing resource details.")

            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            # Validate department
            cursor.execute(
                "SELECT id FROM departments WHERE id = %s",
                (department_id,)
            )

            if not cursor.fetchone():
                raise ValueError("Invalid department.")

            # Insert resource into database
            cursor.execute(
                """
                INSERT INTO resources
                (
                    department_id,
                    name,
                    resource_type,
                    quantity,
                    available_quantity
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    department_id,
                    name,
                    resource_type,
                    quantity,
                    quantity
                )
            )

            connection.commit()

            flash(
                "Resource added successfully!",
                "success"
            )

        except ValueError:
            connection.rollback()

            flash(
                "Please enter valid resource details.",
                "danger"
            )

        except Exception:
            connection.rollback()

            current_app.logger.exception(
                "Resource creation failed"
            )

            flash(
                "Could not add resource. "
                "Check the application log.",
                "danger"
            )

        finally:
            cursor.close()

        return redirect(url_for("admin.resources"))

    try:
        # Fetch departments for dropdown
        cursor.execute(
            """
            SELECT id, name
            FROM departments
            ORDER BY name
            """
        )

        department_list = cursor.fetchall()

        # Fetch resources with department names
        cursor.execute(
            """
            SELECT
                r.id,
                r.name,
                r.resource_type,
                r.quantity,
                r.available_quantity,
                r.department_id,
                d.name AS department_name
            FROM resources r
            JOIN departments d
                ON d.id = r.department_id
            ORDER BY r.id DESC
            """
        )

        resource_list = cursor.fetchall()

    finally:
        cursor.close()

    return render_template(
        "admin/resources.html",
        departments=department_list,
        resources=resource_list
    )
# ==========================================
# COMPLAINT ASSIGNMENT
# ==========================================

@admin_bp.route("/complaints")
@role_required("admin")
def complaint_assignments():

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        # Fetch complaints and their current assigned officers
        cursor.execute("""
            SELECT
                c.id,
                c.title,
                c.category,
                c.status,
                c.department_id,
                c.created_at,
                citizen.full_name AS citizen_name,
                d.name AS department_name,
                assigned.full_name AS officer_name
            FROM complaints c
            JOIN users citizen
                ON citizen.id = c.citizen_id
            LEFT JOIN departments d
                ON d.id = c.department_id
            LEFT JOIN users assigned
                ON assigned.id = c.assigned_officer_id
            ORDER BY c.created_at DESC
        """)

        complaint_list = cursor.fetchall()

        # Fetch active officers and their departments
        cursor.execute("""
            SELECT
                u.id,
                u.full_name,
                e.department_id
            FROM users u
            JOIN employees e
                ON e.user_id = u.id
            WHERE u.role = 'officer'
              AND e.active = TRUE
            ORDER BY u.full_name
        """)

        officer_list = cursor.fetchall()

    finally:
        cursor.close()

    return render_template(
        "admin/complaint_assignments.html",
        complaints=complaint_list,
        officers=officer_list
    )


# ==========================================
# ASSIGN COMPLAINT TO OFFICER
# ==========================================

@admin_bp.route(
    "/complaints/assign/<int:complaint_id>",
    methods=["POST"]
)
@role_required("admin")
def assign_complaint(complaint_id):

    connection = current_app.extensions["mysql"].connection
    cursor = connection.cursor()

    try:
        officer_value = request.form.get("officer_id", "").strip()

        if not officer_value:
            flash("Please select an officer.", "danger")
            return redirect(url_for("admin.complaint_assignments"))

        try:
            officer_id = int(officer_value)
        except ValueError:
            flash("Invalid officer selected.", "danger")
            return redirect(url_for("admin.complaint_assignments"))

        # Check complaint and get its department
        cursor.execute("""
            SELECT id, department_id, status
            FROM complaints
            WHERE id = %s
        """, (complaint_id,))

        complaint = cursor.fetchone()

        if not complaint:
            flash("Complaint not found.", "danger")
            return redirect(url_for("admin.complaint_assignments"))

        if complaint["status"] in ("Resolved", "Rejected"):
            flash(
                "Resolved or rejected complaints cannot be assigned.",
                "warning"
            )
            return redirect(url_for("admin.complaint_assignments"))

        if complaint["department_id"] is None:
            flash(
                "This complaint does not have a department.",
                "danger"
            )
            return redirect(url_for("admin.complaint_assignments"))

        # Check that selected officer belongs to the same department
        cursor.execute("""
            SELECT u.id
            FROM users u
            JOIN employees e
                ON e.user_id = u.id
            WHERE u.id = %s
              AND u.role = 'officer'
              AND e.department_id = %s
              AND e.active = TRUE
        """, (officer_id, complaint["department_id"]))

        officer = cursor.fetchone()

        if not officer:
            flash(
                "Please select an active officer from the complaint's department.",
                "danger"
            )
            return redirect(url_for("admin.complaint_assignments"))

        # Save assignment and update status
        cursor.execute("""
            UPDATE complaints
            SET assigned_officer_id = %s,
                status = 'Assigned'
            WHERE id = %s
        """, (officer_id, complaint_id))

        connection.commit()

        flash("Complaint assigned successfully!", "success")

    except Exception:
        connection.rollback()
        current_app.logger.exception("Complaint assignment failed")
        flash("Could not assign complaint. Please try again.", "danger")

    finally:
        cursor.close()

    return redirect(url_for("admin.complaint_assignments"))
