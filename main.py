import requests
import os
from methods import get_odds_for_sessions, determine_winner, print_winners
from datetime import datetime

API_KEY = os.getenv('KEY')
SPORT = 'upcoming'
REGIONS = 'au' 
MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited
ODDS_FORMAT = 'decimal'
DATE_FORMAT = 'iso' # iso | unix
SPORTS_KEY = 'aussierules_afl'

class game_odds:
    def __init__(self, home_team, away_team, game_date):
        self.home_team = home_team
        self.away_team = away_team
        self.game_date = game_date
        self.home_odds={}
        self.away_odds={} 
        self.home_avg_odds = 0
        self.away_avg_odds = 0
        self.odds_spread = 0
        self.predicted_winner = ""
        self.predicted_loser = ""    
        self.predicted_winner_odds = 0
        self.predicted_loser_odds = 0

sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports', 
    params={
        'api_key': API_KEY
    }
)

if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

for sport in sports_response.json():
    if sport['key'] == SPORTS_KEY:
        afl_obj = sport
        SPORT = afl_obj['key']

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

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

else:
    odds_json = odds_response.json()
    print('--------------------------PREDICATIONS ARE BELOW PEASANTS-----------------------------------')
    print('Number of games:', len(odds_json))
    games = get_odds_for_sessions(game_odds, odds_json)
    games = determine_winner(games)
    print_winners(games)

    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])
