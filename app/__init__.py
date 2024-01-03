from flask import Flask

from app.api import api
from app.blueprints.auth import auth
from app.blueprints.command import command
from app.blueprints.error import error
from app.blueprints.talk import talk
from app.blueprints.user import user
from app.config import Config
from app.extensions import bootstrap, db, login, moment


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app: Flask):
    db.init_app(app)
    bootstrap.init_app(app)
    login.init_app(app)
    moment.init_app(app)


def register_blueprints(app: Flask):
    app.register_blueprint(command)
    app.register_blueprint(error)
    app.register_blueprint(talk)
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(auth, url_prefix="/auth")
