import requests
import json
import os
from datetime import datetime, timedelta

API_KEY = '26d3b5add4msh11d7911c21ce945p14a3a4jsna48caf83e346'
API_HOST = 'flashscore4.p.rapidapi.com'

def fetch_matches_by_date(date_str):
    url = 'https://flashscore4.p.rapidapi.com/api/flashscore/v2/matches/list-by-date'
    
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    
    params = {
        'sport_id': '1',
        'date': date_str,
        'timezone': 'Europe/Berlin'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict) and data.get('error'):
            msg = data.get('message', 'Unknown error')
            print(f'  X {date_str}: {msg}')
            return []
        
        matches = []
        
        if isinstance(data, list):
            for tournament in data:
                if 'matches' in tournament:
                    for match in tournament['matches']:
                        status = match.get('match_status', {})
                        if status.get('is_finished'):
                            odds = match.get('odds', {})
                            scores = match.get('scores', {})
                            
                            if odds and isinstance(odds, dict) and scores:
                                odds_1 = odds.get('1')
                                odds_x = odds.get('X')
                                odds_2 = odds.get('2')
                                
                                if odds_1 and odds_x and odds_2:
                                    match_data = {
                                        'date': date_str,
                                        'home_team': match['home_team']['name'],
                                        'away_team': match['away_team']['name'],
                                        'home_score': scores.get('home', 0),
                                        'away_score': scores.get('away', 0),
                                        'odds_home': float(odds_1),
                                        'odds_draw': float(odds_x),
                                        'odds_away': float(odds_2),
                                        'league': tournament.get('name', 'Unknown'),
                                        'match_id': match.get('match_id')
                                    }
                                    matches.append(match_data)
        
        print(f'  OK {date_str}: {len(matches)} matches')
        return matches
        
    except Exception as e:
        print(f'  X {date_str}: {str(e)}')
        return []

def download_recent_matches(days=7):
    print(f'Downloading matches from last {days} days...')
    print('')
    
    all_matches = []
    today = datetime.now()
    
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        matches = fetch_matches_by_date(date_str)
        all_matches.extend(matches)
    
    print('')
    print(f'Total: {len(all_matches)} matches')
    
    output_file = 'data/historical_matches.json'
    os.makedirs('data', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)
    
    print(f'Saved to {output_file}')
    
    return all_matches

def update_teams(matches):
    print('')
    print('Updating team statistics...')
    
    teams_file = 'data/teams.json'
    
    try:
        with open(teams_file, 'r', encoding='utf-8') as f:
            teams = json.load(f)
    except:
        teams = {}
    
    team_stats = {}
    
    for match in matches:
        home = match['home_team']
        away = match['away_team']
        home_score = match['home_score']
        away_score = match['away_score']
        
        for team in [home, away]:
            if team not in team_stats:
                team_stats[team] = {
                    'goals_scored': 0,
                    'goals_conceded': 0,
                    'matches': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0
                }
        
        team_stats[home]['goals_scored'] += home_score
        team_stats[home]['goals_conceded'] += away_score
        team_stats[home]['matches'] += 1
        
        team_stats[away]['goals_scored'] += away_score
        team_stats[away]['goals_conceded'] += home_score
        team_stats[away]['matches'] += 1
        
        if home_score > away_score:
            team_stats[home]['wins'] += 1
            team_stats[away]['losses'] += 1
        elif home_score == away_score:
            team_stats[home]['draws'] += 1
            team_stats[away]['draws'] += 1
        else:
            team_stats[home]['losses'] += 1
            team_stats[away]['wins'] += 1
    
    updated = 0
    
    for team_name, stats in team_stats.items():
        if stats['matches'] > 0:
            attack = stats['goals_scored'] / stats['matches']
            defense = stats['goals_conceded'] / stats['matches']
            win_rate = stats['wins'] / stats['matches']
            form = win_rate
            elo = 1500 + (win_rate - 0.5) * 400
            
            from ai.models.team_engine import normalize
            team_key = normalize(team_name)
            
            if team_key in teams:
                old_m = teams[team_key].get('matches', 0)
                old_a = teams[team_key].get('attack', 1.0)
                old_d = teams[team_key].get('defense', 1.0)
                old_e = teams[team_key].get('elo', 1500)
                
                total = old_m + stats['matches']
                w_old = old_m / total if total > 0 else 0
                w_new = stats['matches'] / total if total > 0 else 1
                
                teams[team_key] = {
                    'attack': round(old_a * w_old + attack * w_new, 4),
                    'defense': round(old_d * w_old + defense * w_new, 4),
                    'form': round(form, 4),
                    'elo': round(old_e * w_old + elo * w_new, 2),
                    'matches': total
                }
            else:
                teams[team_key] = {
                    'attack': round(attack, 4),
                    'defense': round(defense, 4),
                    'form': round(form, 4),
                    'elo': round(elo, 2),
                    'matches': stats['matches']
                }
            
            updated += 1
    
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    
    print(f'Updated {updated} teams')
    print(f'Total teams: {len(teams)}')
    
    total = len(matches)
    home_w = sum(1 for m in matches if m['home_score'] > m['away_score'])
    draws = sum(1 for m in matches if m['home_score'] == m['away_score'])
    away_w = sum(1 for m in matches if m['home_score'] < m['away_score'])
    
    print('')
    print('Match statistics:')
    print(f'  Home wins: {home_w} ({home_w/total*100:.1f}%)')
    print(f'  Draws: {draws} ({draws/total*100:.1f}%)')
    print(f'  Away wins: {away_w} ({away_w/total*100:.1f}%)')
    
    return teams

if __name__ == '__main__':
    matches = download_recent_matches(days=7)
    
    if matches:
        teams = update_teams(matches)
        print('')
        print('COMPLETE!')
        print(f'  {len(matches)} matches processed')
        print(f'  {len(teams)} teams updated')
    else:
        print('')
        print('No matches found!')
