import requests

def get_ranking_data(userNetID, sessionSecret, rowCount=100):
    API_URL = "http://live.surajang.com:6557/ranking/getTopRankN"
    params = {
        "userNetID": userNetID,
        "sessionSecret": sessionSecret,
        "region": "ES",
        "rankingType": 1,
        "champType": 0,
        "teamMode": 1,
        "rowCount": rowCount
    }

    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()