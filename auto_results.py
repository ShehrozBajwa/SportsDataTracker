from serpapi import GoogleSearch
import json

def get_game_winner(api_response):
    game_spotlight = api_response["sports_results"]
    stage = game_spotlight["game_spotlight"]["stage"]
    
    if stage != "Final":
        return ""

    team1_name = game_spotlight["game_spotlight"]["teams"][0]["name"]
    team1_score = int(game_spotlight["game_spotlight"]["teams"][0]["score"])
    team2_name = game_spotlight["game_spotlight"]["teams"][1]["name"]
    team2_score = int(game_spotlight["game_spotlight"]["teams"][1]["score"])

    # Determine the winner based on scores
    if team1_score > team2_score:
        return team1_name
    elif team2_score > team1_score:
        return team2_name
    else:
        return "It's a tie!"


def get_game_result(query):
    # Set up SerpApi client
    f = open("credentials.json")
    data = json.load(f)
    api_key = data[1]["api_token"]
    params = {
        "q": query,
        "hl": "en",  # Set the language to English
        "gl": "us",  # Set the country to the United States
        "device": "desktop",
        "api_key": api_key
    }
    client = GoogleSearch(params)

    # Perform the search
    result = client.get_json()
    try:
        winner = get_game_winner(result)
    except:
        winner = ""
    f.close()
    return winner

get_game_result("vef")