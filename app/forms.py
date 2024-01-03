from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    EmailField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import URL, DataRequired, Length, Optional


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class ProfileForm(FlaskForm):
    name = StringField("Name", validators=[Optional(), Length(1, 64)])
    location = StringField("Location", validators=[Optional(), Length(1, 64)])
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")


class TalkForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 128)])
    description = TextAreaField("Description")
    slides = StringField("Slides Embed Code (450 pixels wide)")
    video = StringField("Video Embed Code (450 pixels wide)")
    venue = StringField("Venue", validators=[DataRequired(), Length(1, 128)])
    venue_url = StringField("Venue URL", validators=[Optional(), Length(1, 128), URL()])
    date = DateField("Date")
    submit = SubmitField("Submit")

    def from_model(self, model):
        for field in (
            "title",
            "description",
            "slides",
            "video",
            "venue",
            "venue_url",
            "date",
        ):
            if getattr(model, field):
                self[field].data = getattr(model, field)

    def to_model(self, model):
        for field in (
            "title",
            "description",
            "slides",
            "video",
            "venue",
            "venue_url",
            "date",
        ):
            if field in self:
                setattr(model, field, self[field].data)


class PresenterCommentForm(FlaskForm):
    body = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 64)])
    email = EmailField("Email", validators=[DataRequired(), Length(1, 64)])
    body = TextAreaField("Comment", validators=[DataRequired()])
    notify = BooleanField("Notify when new comments are posted", default=True)
    submit = SubmitField("Submit")
