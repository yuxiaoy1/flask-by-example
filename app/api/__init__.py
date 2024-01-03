from flask import Blueprint, g, request

from app.models import User

api = Blueprint("api", __name__)

from app.api import comment, error  # noqa: E402, F401
from app.api.error import bad_request, unauthorized  # noqa: E402


@api.before_request
def before_api_request():
    if request.json is None:
        return bad_request("Invalid json in body.")
    token = request.json.get("token")
    if not token:
        return unauthorized("Authentication token not provided.")
    user = User.check_api_token(token)
    if not user:
        return unauthorized("Invalid authentication token.")
    g.current_user = user
