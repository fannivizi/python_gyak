"""Flask alkalmazás"""

from flask import render_template, request, flash, redirect, session, url_for
from python_gyak.models import Watched, API, UserManager, WatchedManager
from python_gyak import create_app

app = create_app()

api = API()
user = UserManager()
watched = WatchedManager()


@app.route('/')
def index():
    """főoldal"""
    tv_shows = api.get_all(10)
    return render_template("index.html", shows=tv_shows)


@app.route('/shows')
def shows():
    """sorozatok oldal"""
    tv_shows = api.get_all()
    return render_template("shows.html", shows=tv_shows)


@app.route('/show/<show_id>')
def show(show_id):
    """egy sorozat oldala"""
    if 'username' in session:
        watched_ids = [w.id for w in Watched.query.filter_by(
            username=session['username']).all()]
    else:
        watched_ids = []

    tv_show = api.get_show(show_id)
    seasons = api.get_episodes(show_id)

    return render_template("show.html",
                           show=tv_show, seasons=seasons, watched=watched_ids)


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    """regisztráció"""
    if 'username' in session:
        return redirect(url_for('index'))

    error = ""
    if request.method == 'POST':
        error = user.register(request.form['username'],
                              request.form['email'],
                              request.form['password'])

        if error == "":
            flash("Sikeres regisztráció")
            return redirect("/")

    return render_template('reg.html', error=error)


@app.route('/login', methods=['POST'])
def login():
    """bejelentkezés"""
    if 'username' in session:
        return redirect(url_for('index'))

    message = user.login(request.form['username'], request.form['password'])

    flash(message)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """kijelentkezés"""
    if 'username' not in session:
        return redirect(url_for('index'))

    user.logout()
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    """profil oldal"""
    if 'username' not in session:
        return redirect(url_for('index'))

    episodes = watched.get_all(session['username'])
    stats = watched.stats(session['username'])

    return render_template('profile.html',
                           user=user.get_user(), episodes=episodes, stats=stats)


@app.route('/add_watched/<show_id>')
def add_watched(show_id):
    """megnézett epizód hozzáadása az adatbázishoz"""
    if 'username' not in session:
        return redirect(url_for('index'))

    watched.add(show_id, session['username'])

    return redirect(request.referrer or url_for('index'))


if __name__ == '__main__':
    app.run()
