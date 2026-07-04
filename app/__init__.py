import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "mypartpicker-secret-key-2024"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mypartpicker.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # profile picture uploads
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path, "static", "uploads", "profile_pics"
    )
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
    app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "webp"}
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from app.routes.parts import parts

    app.register_blueprint(parts)

    from app.routes.auth import auth

    app.register_blueprint(auth)

    from app.routes.builds import builds

    app.register_blueprint(builds)

    from app.routes.admin import admin

    app.register_blueprint(admin)

    with app.app_context():
        db.create_all()

    return app
