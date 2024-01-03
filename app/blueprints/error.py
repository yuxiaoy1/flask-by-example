from flask import Blueprint

error = Blueprint("error", __name__)


@error.app_errorhandler(400)
def bad_request():
    return "bad request", 400
