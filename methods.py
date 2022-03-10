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
            game.odds_spread = game.away_avg_odds - game.home_avg_odds
        else:
            game.predicted_winner = game.home_team
            game.odds_spread = game.home_avg_odds - game.away_avg_odds
    return games