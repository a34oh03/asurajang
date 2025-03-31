from flask import Flask, render_template
from ranking.api import get_ranking_data
from ranking.utils import parse_players, calculate_champion_stats

app = Flask(__name__)

@app.route('/')
def index():
    import os
    userNetID = os.environ.get("userNetID")
    sessionSecret = os.environ.get("sessionSecret")

    try:
        data = get_ranking_data(userNetID, sessionSecret)
        players_data = data["data"]["players"]
        players = parse_players(players_data)
        champion_stats = calculate_champion_stats(players_data)

        return render_template("index.html", players=players, champion_stats=champion_stats)

    except Exception as e:
        
        return render_template("index.html", error=True)


if __name__ == '__main__':
    app.run(debug=True)