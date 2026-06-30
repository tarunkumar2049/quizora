import os

from dotenv import load_dotenv
load_dotenv()

import mysql.connector
from flask import Flask, jsonify, render_template

from config import config_by_name
from extensions import bcrypt, login_manager


def create_app():
    """Create and configure the Flask application."""

    app_env = os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(app_env, config_by_name["development"]))

    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from models.user_model import get_user_by_id

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/db-check")
    def db_check():
        """Simple database connectivity check for local setup verification."""
        return jsonify(app.config["MYSQL_CONFIG"])

        try:
            connection = mysql.connector.connect(**app.config["MYSQL_CONFIG"])
            connection.close()
            return jsonify({"database": "connected"})
        except mysql.connector.Error as error:
            return jsonify({"database": "not connected", "error": str(error)}), 500

    from routes.analytics_routes import analytics_bp
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.performance_routes import performance_bp
    from routes.quiz_routes import quiz_bp

    app.register_blueprint(analytics_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(performance_bp)
    app.register_blueprint(quiz_bp)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("errors/500.html"), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
