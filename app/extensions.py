from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bootstrap = Bootstrap5()
moment = Moment()
login = LoginManager()
login.login_view = "auth.login"
login.login_message_category = "warning"


@login.user_loader
def load_user(id):
    from app.models import User

    return db.session.get(User, id)
