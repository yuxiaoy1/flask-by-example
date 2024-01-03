import click
from flask import Blueprint

from app.extensions import db
from app.models import User

command = Blueprint("command", __name__, cli_group=None)


@command.cli.command()
def initdb():
    """Create database."""
    db.drop_all()
    db.create_all()
    print("Database created.")


@command.cli.command()
@click.option("--username", prompt=True, help="The username used to login.")
@click.option("--email", prompt=True, help="The email used to login.")
@click.option(
    "--admin",
    prompt=True,
    default=False,
    help="Set user to admin.",
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="The password used to login.",
)
def adduser(username, email, password, admin):
    """Register a new user."""
    user = db.session.scalar(db.select(User).filter_by(username=username))
    if user is not None:
        user.email = email
        user.password = password
        user.is_admin = admin
    else:
        user = User(username=username, email=email, password=password, is_admin=admin)
    db.session.add(user)
    db.session.commit()
    print(f"User {username} was created successfully.")
