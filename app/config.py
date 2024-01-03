import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "topsecret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "db.sqlite")
    )
    SQLALCHEMY_EHCO = True

    TALKS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10
