from audioop import avg
from turtle import home
import requests
import os

# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = os.getenv('KEY')

SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'au' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'decimal' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

class game_odds:
    def __init__(self, home_team, away_team, game_date):
        self.home_team = home_team
        self.away_team = away_team
        self.game_date = game_date
        self.home_odds={}
        self.away_odds={} 
        self.home_avg_odds = 0
        self.away_avg_odds = 0
        self.predicted_winner = ""


    

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# First get a list of in-season sports
#   The sport 'key' from the response can be used to get odds in the next request
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports', 
    params={
        'api_key': API_KEY
    }
)


if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

else:
    print('List of in season sports:', sports_response.json())


global afl_obj
for sport in sports_response.json():
    if sport['key'] == 'aussierules_afl':
        afl_obj = sport
        SPORT = afl_obj['key']

print(afl_obj)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# This will deduct from the usage quota
# The usage quota cost = [number of markets specified] x [number of regions specified]
# For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

odds_response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
    params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    }
)

def get_odds_for_sessions(game_odds, odds_json):
    games = []
    for game in odds_json:        
        home_team = game['home_team']
        away_team = game['away_team']
        game_date = game['commence_time']
        game_odds_collection = game_odds(home_team, away_team, game_date)
        for bookkeeper in game['bookmakers']:
            outcomes = bookkeeper['markets'][0]['outcomes']
            for outcome in outcomes:
                if outcome['name'] == home_team:
                    game_odds_collection.home_odds[bookkeeper['title']] = outcome['price']
                else:
                    game_odds_collection.away_odds[bookkeeper['title']] = outcome['price']
        games.append(game_odds_collection)
    return games

def determine_winner(games):
    for game in games:
        away_odds = game.away_odds.values()
        home_odds = game.home_odds.values()
        game.away_avg_odds = sum(away_odds)/len(away_odds)
        game.home_avg_odds = sum(home_odds)/len(home_odds)

        if game.away_avg_odds > game.home_avg_odds:
            game.predicted_winner = game.away_team
        else:
            game.predicted_winner = game.home_team
    return games

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

else:
    odds_json = odds_response.json()
    print('Number of events:', len(odds_json))
    games = get_odds_for_sessions(game_odds, odds_json)
    games = determine_winner(games)

    print(games)
 
    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])
