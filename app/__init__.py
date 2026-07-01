from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mypartpicker-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mypartpicker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    from app.routes.auth import auth
    app.register_blueprint(auth)

    # Uncomment as each member finishes their section:
    # from app.routes.parts import parts
     #app.register_blueprint(parts)
     #from app.routes.builds import builds
     #app.register_blueprint(builds)
     #from app.routes.admin import admin
     #app.register_blueprint(admin)

    with app.app_context():
        db.create_all()

    return app
