import requests
from flask import Flask, render_template

app = Flask(__name__)

def best_rated(tv_shows):
    return sorted([s for s in tv_shows if s['weight']],
                    key=lambda s: s['weight'],
                    reverse=True)

@app.route('/')
def landing():
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


if __name__ == '__main__':
    app.run()
