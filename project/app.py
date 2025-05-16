import os
import requests
from flask import Flask, render_template, request, flash, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Watched, API, UserManager, WatchedManager

api = API()
user = UserManager()
watched = WatchedManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = '\x92\x8e(\x145\x8b\xcdti\xed\xd4y'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'users.db')}"
db.init_app(app)
with app.app_context():
    db.create_all()

def best_rated(tv_shows):
    tv_shows.sort(key=lambda show: show['weight'], reverse=True)
    return tv_shows

@app.route('/')
def index():
    tv_shows = api.get_all(10)
    return render_template("index.html", shows=tv_shows)

@app.route('/shows')
def shows():
    tv_shows = api.get_all()
    return render_template("shows.html", shows=tv_shows)

@app.route('/show/<show_id>')
def show(show_id):
    if 'username' in session:
        watched = [w.id for w in Watched.query.filter_by(username=session['username']).all()]
    else:
        watched = []

    tv_show = api.get_show(show_id)
    seasons = api.get_episodes(show_id)

    return render_template("show.html", show=tv_show, seasons=seasons, watched=watched)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if 'username' in session:
        return redirect(url_for('index'))

    error = ""
    if request.method == 'POST':
        error = user.register(request.form['username'], request.form['email'], request.form['password'])

        if error == "":
            flash("Sikeres regisztráció")
            return redirect("/")

    return render_template('reg.html', error=error)

@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    message = user.login(request.form['username'], request.form['password'])

    flash(message)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if 'username' not in session:
        return redirect(url_for('index'))

    user.logout()
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))

    episodes = watched.get_all(session['username'])
    stats = watched.stats(session['username'])

    return render_template('profile.html', user=user.get_user(), episodes=episodes, stats=stats)

@app.route('/add_watched/<show_id>')
def add_watched(show_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    watched.add(show_id, session['username'])

    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run()
