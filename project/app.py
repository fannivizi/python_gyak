import os
import requests
from flask import Flask, render_template, request, flash, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Watched

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
    response = requests.get("https://api.tvmaze.com/shows")
    if response.status_code == 200:
        tv_shows = best_rated(response.json())[:10]
    else:
        tv_shows = []
    return render_template("index.html", shows=tv_shows)

@app.route('/shows')
def shows():
    response = requests.get("https://api.tvmaze.com/shows")
    if response.status_code == 200:
        tv_shows = best_rated(response.json())
    else:
        tv_shows = []
    return render_template("shows.html", shows=tv_shows)

@app.route('/show/<show_id>')
def show(show_id):
    tv_show = requests.get(f"https://api.tvmaze.com/shows/{show_id}").json()

    episodes = requests.get(f"https://api.tvmaze.com/shows/{show_id}/episodes").json()
    seasons = {}
    for episode in episodes:
        if episode['season'] in seasons:
            seasons[episode['season']].append(episode)
        else:
            seasons[episode['season']] = [episode]

    return render_template("show.html", show=tv_show, seasons=seasons)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if 'username' in session:
        return redirect(url_for('index'))

    error = ""

    if request.method == 'POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']

        if username.strip() == "" or email.strip() == "" or password.strip() == "":
            error = "Adj meg minden adatot!"
        elif User.query.filter_by(username=username).first():
            error = "A felhasználónév foglalt."
        elif User.query.filter_by(email=email).first():
            error = "Az email cím már foglalt."

        if error == "":
            pw = generate_password_hash(password)
            db.session.add(User(username=username, email=email, password=pw))
            db.session.commit()
            flash("Sikeres regisztráció")
            return redirect("/")

    return render_template('reg.html', error=error)

@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['username'] = user.username
        flash("Sikeres bejelentkezés")
        return redirect(url_for('index'))

    flash("Hibás felhasználónév vagy jelszó")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if 'username' not in session:
        return redirect(url_for('index'))

    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))

    user = User.query.filter_by(username=session['username']).first()
    watched = Watched.query.filter_by(username=session['username']).all()

    episodes = []
    for episode in watched:
        episodes.append(requests.get(f"https://api.tvmaze.com/episodes/{episode.id}?embed=show").json())

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

    return render_template('profile.html', user=user, episodes=episodes, stats=stats)

@app.route('/add_watched/<id>')
def add_watched(id):
    if 'username' not in session:
        return redirect(url_for('index'))

    username=session['username']

    watched=Watched(id=id, username=username)
    db.session.add(watched)
    db.session.commit()

    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run()
