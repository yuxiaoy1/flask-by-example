from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm
from app.models import User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("talk.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(username=form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next = request.args.get("next")
        if not next or urlsplit(next).netloc != "":
            next = url_for("talk.index")
        return redirect(next)
    return render_template("auth/login.html", form=form)


@auth.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("talk.index"))
