from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import ProfileForm
from app.models import Talk, User

user = Blueprint("user", __name__)


@user.get("/<username>")
@login_required
def index(username):
    user = db.session.scalar(db.select(User).filter_by(username=username)) or abort(404)
    talks = db.paginate(
        user.talks.select().order_by(Talk.date.desc()),
        per_page=current_app.config["TALKS_PER_PAGE"],
    )
    return render_template("user/index.html", user=user, talks=talks)


@user.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Your profile has been updated.", "info")
        return redirect(url_for("user.index", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template("user/profile.html", form=form)
