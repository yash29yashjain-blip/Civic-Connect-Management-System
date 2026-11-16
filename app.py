
from flask import Flask, render_template
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MySQL with the application settings
    app.config["MYSQL_HOST"] = Config.MYSQL_HOST
    app.config["MYSQL_USER"] = Config.MYSQL_USER
    app.config["MYSQL_PASSWORD"] = Config.MYSQL_PASSWORD
    app.config["MYSQL_DB"] = Config.MYSQL_DB
    app.config["MYSQL_PORT"] = Config.MYSQL_PORT
    app.config["MYSQL_CURSORCLASS"] = Config.MYSQL_CURSORCLASS

    mysql.init_app(app)
    app.extensions["mysql"] = mysql

    from routes.auth import auth_bp
    from routes.citizen import citizen_bp
    from routes.officer import officer_bp
    from routes.admin import admin_bp
    from routes.complaints import complaints_bp
    from routes.reports import reports_bp
    from routes.os_simulation import os_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(officer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(os_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
