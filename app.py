import os
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
    userNetID = os.environ.get("userNetID")
    sessionSecret = os.environ.get("sessionSecret")

    try:
        # 솔로 모드
        solo_data = get_ranking_data(userNetID, sessionSecret, teamMode=1)
        solo_players_data = solo_data["data"]["players"]
        solo_players = parse_players(solo_players_data)
        solo_stats = calculate_champion_stats(solo_players_data)

        # 트리오 모드
        trio_data = get_ranking_data(userNetID, sessionSecret, teamMode=2)
        trio_players_data = trio_data["data"]["players"]
        trio_players = parse_players(trio_players_data)
        trio_stats = calculate_champion_stats(trio_players_data)

        return render_template(
            "index.html",
            solo_players=solo_players,
            trio_players=trio_players,
            solo_stats=solo_stats,
            trio_stats=trio_stats
        )
            
    except Exception as e:
        
        return render_template("index.html", error=True)

@app.before_request
def limit_static():
    if request.path.startswith("/static/"):
        limiter.limit("45 per minute")(lambda: None)()

if __name__ == '__main__':
    app.run(debug=True)