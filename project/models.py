import requests
from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from werkzeug.security import generate_password_hash, check_password_hash

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

class API:
    url = "https://api.tvmaze.com"

    def get_all(self, top = 0):
        response = requests.get(f"{self.url}/shows")
        if response.status_code != 200:
            return []

        tv_shows = response.json()
        tv_shows = sorted(tv_shows, key=lambda show: show['weight'], reverse=True)

        if top != 0: return tv_shows[:top]
        return tv_shows

    def get_show(self, show_id):
        response = requests.get(f"{self.url}/shows/{show_id}")
        if response.status_code != 200:
            return {}
        return response.json()

    def get_episodes(self, show_id):
        response = requests.get(f"{self.url}/shows/{show_id}/episodes")
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
        response = requests.get(f"{self.url}/episodes/{episode_id}?embed=show")
        if response.status_code != 200:
            return {}
        return response.json()

class UserManager:
    username = None
    email = None

    @staticmethod
    def register(username, email, password):
        if username.strip() == "" or email.strip() == "" or password.strip() == "":
            return "Adj meg minden adatot!"
        elif User.query.filter_by(username=username).first():
            return "A felhasználónév foglalt."
        elif User.query.filter_by(email=email).first():
            return "Az email cím már foglalt."

        pw = generate_password_hash(password)
        db.session.add(User(username=username, email=email, password=pw))
        db.session.commit()

        return ""

    def login(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            self.username = user.username
            self.email = user.email
            return "Sikeres bejelentkezés"
        return "Hibás felhasználónév vagy jelszó"

    def logout(self):
        session.pop('username', None)
        self.username = None
        self.email = None

    def get_user(self):
        return {"username": self.username, "email": self.email}

class WatchedManager:
    api = API()

    def add(self, show_id, username):
        watched = Watched(id=show_id, username=username)
        db.session.add(watched)
        db.session.commit()

    def get_all(self, username):
        watched = Watched.query.filter_by(username=session['username']).all()

        episodes = []
        for episode in watched:
            episodes.append(self.api.get_episode(episode.id))

        return episodes

    def stats(self, username):
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
