from flask import Flask, render_template
from ranking.api import get_ranking_data
from ranking.utils import parse_players, calculate_champion_stats
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["45 per minute"]
)

@app.route('/')
def index():
    userNetID = "76561198112838034"
    sessionSecret = "fa2926c57cec0fd2a4c9d3b9c9650ad1"

    try:
        data = get_ranking_data(userNetID, sessionSecret)
        players_data = data["data"]["players"]
        players = parse_players(players_data)
        champion_stats = calculate_champion_stats(players_data)

        return render_template("index.html", players=players, champion_stats=champion_stats)

    except Exception as e:
        
        return render_template("index.html", error=True)

@app.before_request
def limit_static():
    if request.path.startswith("/static/"):
        limiter.limit("45 per minute")(lambda: None)()

if __name__ == '__main__':
    app.run(debug=True)