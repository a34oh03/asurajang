from flask import Flask, render_template
from ranking.api import get_ranking_data
from ranking.utils import parse_players, calculate_champion_stats

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)