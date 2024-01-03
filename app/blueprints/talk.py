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
from app.forms import CommentForm, PresenterCommentForm, TalkForm
from app.models import Comment, Talk

talk = Blueprint("talk", __name__)


@talk.get("/")
@login_required
def index():
    talks = db.paginate(
        db.select(Talk).order_by(Talk.date.desc()),
        per_page=current_app.config["TALKS_PER_PAGE"],
    )
    return render_template("talk/index.html", talks=talks)


@talk.route("/talk/new", methods=["GET", "POST"])
@login_required
def new_talk():
    form = TalkForm()
    if form.validate_on_submit():
        talk = Talk(
            title=form.title.data,
            description=form.description.data,
            slides=form.slides.data,
            video=form.video.data,
            venue=form.venue.data,
            venue_url=form.venue_url.data,
            date=form.date.data,
            author=current_user,
        )
        db.session.add(talk)
        db.session.commit()
        flash("The talk was added successfully.", "info")
        return redirect(url_for("talk.index"))
    return render_template("talk/new_talk.html", form=form)


@talk.route("/talk/<int:id>", methods=["GET", "POST"])
def get_talk(id):
    talk = db.get_or_404(Talk, id)
    comment = None
    if current_user.is_authenticated:
        form = PresenterCommentForm()
        if form.validate_on_submit():
            comment = Comment(
                body=form.body.data,
                talk=talk,
                author=current_user,
                notify=False,
                approved=True,
            )
    else:
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(
                body=form.body.data,
                talk=talk,
                author_name=form.name.data,
                author_email=form.email.data,
                notify=form.notify.data,
                approved=False,
            )
    if comment:
        db.session.add(comment)
        db.session.commit()
        flash(
            "Your comment has been published."
            if comment.approved
            else "Your comment will be published after it's reviewed by the presenter.",
            "info",
        )
        return redirect(url_for("talk.get_talk", id=talk.id))
    comments = db.paginate(
        talk.comments.select().order_by(Comment.timestamp.asc()),
        per_page=current_app.config["COMMENTS_PER_PAGE"],
    )
    return render_template("talk/talk.html", talk=talk, form=form, comments=comments)


@talk.route("/talk/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_talk(id):
    talk = db.get_or_404(Talk, id)
    if not current_user.is_admin and current_user != talk.author:
        abort(404)
    form = TalkForm()
    if form.validate_on_submit():
        form.to_model(talk)
        db.session.commit()
        flash("The talk was updated successfully.", "info")
        return redirect(url_for("talk.get_talk", id=talk.id))
    form.from_model(talk)
    return render_template("talk/edit_talk.html", form=form)


@talk.get("/moderate")
@login_required
def moderate():
    comments = db.paginate(
        current_user.for_moderation().order_by(Comment.timestamp.asc()),
        per_page=current_app.config["COMMENTS_PER_PAGE"],
    )
    return render_template("talk/moderate.html", comments=comments)


@talk.get("/moderate-admin")
@login_required
def moderate_admin():
    if not current_user.is_admin:
        abort(403)
    comments = db.paginate(
        current_user.for_moderation(True).order_by(Comment.timestamp.asc()),
        per_page=current_app.config["COMMENTS_PER_PAGE"],
    )
    return render_template("talk/moderate.html", comments=comments)
