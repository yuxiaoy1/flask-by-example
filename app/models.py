from datetime import UTC, datetime
from hashlib import md5
from time import time
from typing import Optional

import jwt
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(unique=True, index=True)
    username: so.Mapped[str] = so.mapped_column(unique=True, index=True)
    is_admin: so.Mapped[bool]
    password_hash: so.Mapped[str]
    name: so.Mapped[Optional[str]]
    location: so.Mapped[Optional[str]]
    bio: so.Mapped[Optional[str]]
    member_since: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(UTC)
    )
    talks: so.WriteOnlyMapped["Talk"] = so.relationship(back_populates="author")
    comments: so.WriteOnlyMapped["Comment"] = so.relationship(back_populates="author")

    def avatar(self, size=128):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return (
            check_password_hash(self.password_hash, password)
            if self.password_hash
            else None
        )

    def get_api_token(self, expires_in=600):
        return jwt.encode(
            {"user": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def check_api_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["user"]
        except Exception:
            return
        return db.session.get(User, id)

    def for_moderation(self, admin=False):
        if admin and self.is_admin:
            return Comment.for_moderation()
        return (
            db.select(Comment)
            .join(Talk, Comment.talk_id == Talk.id)
            .where(sa.and_(Talk.author == self, Comment.approved == False))  # noqa:E712
        )

    def for_moderation_count(self, admin=False):
        return db.session.scalar(
            db.select(sa.func.count()).select_from(self.for_moderation(admin))
        )


class Talk(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    slides: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    video: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    venue: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    venue_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    date: so.Mapped[Optional[datetime]]
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    author: so.Mapped["User"] = so.relationship(back_populates="talks")
    comments: so.WriteOnlyMapped["Comment"] = so.relationship(back_populates="talk")

    def approved_comments(self):
        return db.session.scalars(self.comments.select().filter_by(approved=True))


class Comment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.Text)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(UTC)
    )
    notify: so.Mapped[bool] = so.mapped_column(default=True)
    approved: so.Mapped[bool] = so.mapped_column(default=False)
    user_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("user.id"))
    author: so.Mapped[Optional["User"]] = so.relationship(back_populates="comments")
    author_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    author_email: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    talk_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("talk.id"))
    talk: so.Mapped["Talk"] = so.relationship(back_populates="comments")

    @staticmethod
    def for_moderation():
        return db.select(Comment).filter_by(approved=False)
