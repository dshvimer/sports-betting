import pandas as pd
import requests
from datetime import datetime, date
import matplotlib.pyplot as plt
import time

API_KEY = ""

def get_sports():
    url = "https://odds.p.rapidapi.com/v1/sports"

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "odds.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers)

    return response.json()['data']

def get_odds():
    url = "https://odds.p.rapidapi.com/v1/odds"
    querystring = {"sport":"americanfootball_nfl","region":"us","mkt":"h2h","dateFormat":"iso","oddsFormat":"decimal"}
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "odds.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()['data']

def get_matches():
    odds = get_odds()
    return [game['teams'] for game in odds]

def odds_to_frame(odds):
    frames = []
    for game in odds:
        for i, team in enumerate(game['teams']):
            for site in game['sites']:
                frame = {
                    'team': team,
                    'site': site['site_key'],
                    'odds': site['odds']['h2h'][i],
                    'time': datetime.now()
                }
                frames.append(frame)
    df = pd.DataFrame(frames)
    df = df.set_index('time')
    return df

def latest():
    return odds_to_frame(get_odds())

def game_info(df, teams):
    sites = df['site'].isin(['fanduel', 'draftkings'])
    teams = df['team'].isin(teams)
    df = df[sites & teams]
    df = df.groupby([df.index.hour, df.index.minute, 'team']).mean().unstack()
    df.index.rename(['hour', 'minute'], inplace=True)
    return df['odds']


if __name__ == "__main__":
    df = pd.DataFrame()

    while True:
        print('Running at: ', datetime.now())
        df = pd.concat([df, latest()])
        df.to_csv('2021-01-03.csv')
        time.sleep(60)