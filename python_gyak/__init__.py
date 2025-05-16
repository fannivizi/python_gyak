import os
from flask import Flask
from python_gyak.models import db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '\x92\x8e(\x145\x8b\xcdti\xed\xd4y'

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'users.db')}"

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app