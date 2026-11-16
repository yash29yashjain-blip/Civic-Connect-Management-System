
from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

auth_bp = Blueprint("auth", __name__)


def role_required(*allowed_roles):
    """Protect a route using the signed-in user's role."""
    def decorator(view_function):
        @wraps(view_function)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))

            if session.get("role") not in allowed_roles:
                flash("You do not have permission to access that page.", "danger")
                return redirect(url_for("index"))

            return view_function(*args, **kwargs)
        return wrapped
    return decorator


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not full_name or not email or not password:
            flash("Name, email, and password are required.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return render_template("register.html")

        connection = current_app.extensions["mysql"].connection
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("An account with this email already exists.", "danger")
                return render_template("register.html")

            cursor.execute(
                """INSERT INTO users
                   (full_name, email, password_hash, role, phone, address)
                   VALUES (%s, %s, %s, 'citizen', %s, %s)""",
                (
                    full_name, email,
                    generate_password_hash(password),
                    phone, address
                )
            )
            connection.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            connection.rollback()
            current_app.logger.exception("Registration failed")
            flash("Registration could not be completed.", "danger")
        finally:
            cursor.close()

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = current_app.extensions["mysql"].connection
        cursor = connection.cursor()

        try:
            cursor.execute(
                """SELECT id, full_name, email, password_hash, role
                   FROM users WHERE email=%s""",
                (email,)
            )
            user = cursor.fetchone()
        finally:
            cursor.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            flash("Welcome back!", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            if user["role"] == "officer":
                return redirect(url_for("officer.dashboard"))
            return redirect(url_for("citizen.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))
