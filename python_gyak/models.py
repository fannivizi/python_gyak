"""az alkalmazáshoz szükséges osztályok"""

import requests
from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PrimaryKeyConstraint
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User tábla: felhasználó adatok"""
    username = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Watched(db.Model):
    """Watched tábla: username és megnézett sorozat id-ja"""
    id = db.Column(db.Integer, nullable=False)
    username = db.Column(
        db.String(80),
        db.ForeignKey('user.username'),
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint('id', 'username'),
    )


class API:
    """A tvmaze api kezelését végző osztály"""
    def __init__(self):
        self.url = "https://api.tvmaze.com"

    def get_all(self, top=0):
        """Az összes sorozat lekérése"""
        response = requests.get(f"{self.url}/shows", timeout=10)
        if response.status_code != 200:
            return []

        tv_shows = response.json()
        tv_shows = sorted(tv_shows, key=lambda show: show['weight'], reverse=True)

        if top != 0:
            return tv_shows[:top]
        return tv_shows

    def get_show(self, show_id):
        """egy sorozat adatainak lekérése"""
        response = requests.get(f"{self.url}/shows/{show_id}", timeout=10)
        if response.status_code != 200:
            return {}
        return response.json()

    def get_episodes(self, show_id):
        """egy sorozathoz tartozó részek lekérdezése"""
        response = requests.get(f"{self.url}/shows/{show_id}/episodes", timeout=10)
        if response.status_code != 200:
            return {}

        episodes = response.json()
        seasons = {}

        for episode in episodes:
            if episode['season'] in seasons:
                seasons[episode['season']].append(episode)
            else:
                seasons[episode['season']] = [episode]

        return seasons

    def get_episode(self, episode_id):
        "egy epizód lekérése"
        response = requests.get(f"{self.url}/episodes/{episode_id}?embed=show", timeout=10)
        if response.status_code != 200:
            return {}
        return response.json()


class UserManager:
    """A felhasználók kezelését végző osztály"""
    def __init__(self):
        self.username = None
        self.email = None

    @staticmethod
    def register(username, email, password):
        """regisztráció"""
        if username.strip() == "" or email.strip() == "" or password.strip() == "":
            return "Adj meg minden adatot!"
        if User.query.filter_by(username=username).first():
            return "A felhasználónév foglalt."
        if User.query.filter_by(email=email).first():
            return "Az email cím már foglalt."

        pw = generate_password_hash(password)
        db.session.add(User(username=username, email=email, password=pw))
        db.session.commit()

        return ""

    def login(self, username, password):
        """bejelentkezés"""
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            self.username = user.username
            self.email = user.email
            return "Sikeres bejelentkezés"
        return "Hibás felhasználónév vagy jelszó"

    def logout(self):
        """kijelentkezés"""
        session.pop('username', None)
        self.username = None
        self.email = None

    def get_user(self):
        """felhasználó adatok lekérése"""
        return {"username": self.username, "email": self.email}


class WatchedManager:
    """A megnézett részek kezelését végző osztály"""
    def __init__(self):
        self.api = API()

    @staticmethod
    def add(show_id, username):
        """új rész hozzáadása"""
        watched = Watched(id=show_id, username=username)
        db.session.add(watched)
        db.session.commit()

    def get_all(self, username):
        """a felhasználó összes látott epizódja"""
        watched = Watched.query.filter_by(username=username).all()

        episodes = []
        for episode in watched:
            episodes.append(self.api.get_episode(episode.id))

        return episodes

    def stats(self, username):
        """statisztikák a profil oldalhoz"""
        episodes = self.get_all(username)

        shows = []
        total = 0
        for episode in episodes:
            total += episode['runtime']
            show_id = episode['_embedded']['show']['id']
            if show_id not in shows:
                shows.append(show_id)

        stats = {
            'episodes': len(episodes),
            'shows': len(shows),
            'time': round(total / 60, 1)
        }

        return stats
