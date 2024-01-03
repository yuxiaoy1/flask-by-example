from flask import g

from app.api import api
from app.api.error import bad_request, forbidden
from app.extensions import db
from app.models import Comment


@api.put("/comments/<int:id>")
def approve_comment(id):
    comment = db.get_or_404(Comment, id)
    if comment.talk.author != g.current_user and not g.current_user.is_admin:
        return forbidden("You cannot modify this comment.")
    if comment.approved:
        return bad_request("Comment is already approved.")
    comment.approved = True
    db.session.commit()
    return {"status": "ok"}


@api.delete("/comments/<int:id>")
def delete_comment(id):
    comment = db.get_or_404(Comment, id)
    if comment.talk.author != g.current_user and not g.current_user.is_admin:
        return forbidden("You cannot modify this comment.")
    if comment.approved:
        return bad_request("Comment is already approved.")
    db.session.delete(comment)
    db.session.commit()
    return "", 204
