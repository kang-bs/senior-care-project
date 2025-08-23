# cli.py

from flask import current_app
from models import db, User
import bcrypt
import click
from flask.cli import with_appcontext

def register_cli(app):
    @app.cli.command("db-init")
    @with_appcontext
    def db_init():
        """Initializes the database and creates all tables."""
        db.create_all()
        click.echo("Database initialized and tables created.")

    @app.cli.command("create-admin")
    def create_admin():
        username = input("관리자 아이디: ")
        password = input("비밀번호: ")

        if User.query.filter_by(username=username).first():
            print("이미 존재하는 아이디입니다.")
            return

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        admin_user = User(
            username=username,
            password=hashed_pw.decode("utf-8"),
            nickname="관리자",
            user_type=2
        )
        db.session.add(admin_user)
        db.session.commit()
        print("관리자 계정이 생성되었습니다.")