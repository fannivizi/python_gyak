from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import foreign

db = SQLAlchemy()

class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Watched(db.Model):
    id = db.Column(db.Integer, nullable=False)
    username = db.Column(
        db.String(80),
        db.ForeignKey('user.username'),
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', 'username'),
    )