import json
from collections import defaultdict

print('=' * 60)
print('INTEGRATING DATA-RAW INTO FFPAS SYSTEM')
print('=' * 60)

# Load all data sources
data_files = {
    'data_raw': 'data/data_raw_matches.json',
    'football_json': 'data/football_json_matches.json',
    'historical': 'data/historical_matches.json',
    'european': 'data/european_matches.json',
    'mackolik': 'data/mackolik_matches.json',
    'final_dataset': 'data/final_dataset_matches.json'
}

all_matches = []
for name, file in data_files.items():
    try:
        with open(file, 'r', encoding='utf-8') as f:
            matches = json.load(f)
            all_matches.extend(matches)
            print(f'Loaded {len(matches):,} matches from {name}')
    except Exception as e:
        print(f'Could not load {name}: {e}')

print(f'\nTotal matches: {len(all_matches):,}')

# Analyze team statistics
team_stats = defaultdict(lambda: {
    'home_matches': 0, 'away_matches': 0,
    'home_wins': 0, 'home_draws': 0, 'home_losses': 0,
    'away_wins': 0, 'away_draws': 0, 'away_losses': 0,
    'home_goals_scored': 0, 'home_goals_conceded': 0,
    'away_goals_scored': 0, 'away_goals_conceded': 0,
    'total_matches': 0
})

def normalize(name):
    return name.lower().strip() if name else ''

print('\nAnalyzing team statistics...')
for match in all_matches:
    try:
        home = normalize(match.get('home_team', ''))
        away = normalize(match.get('away_team', ''))
        hs = match.get('home_score')
        as_ = match.get('away_score')
        
        if not home or not away or hs is None or as_ is None:
            continue
        
        # Home team stats
        team_stats[home]['home_matches'] += 1
        team_stats[home]['home_goals_scored'] += hs
        team_stats[home]['home_goals_conceded'] += as_
        team_stats[home]['total_matches'] += 1
        
        # Away team stats
        team_stats[away]['away_matches'] += 1
        team_stats[away]['away_goals_scored'] += as_
        team_stats[away]['away_goals_conceded'] += hs
        team_stats[away]['total_matches'] += 1
        
        # Results
        if hs > as_:
            team_stats[home]['home_wins'] += 1
            team_stats[away]['away_losses'] += 1
        elif hs < as_:
            team_stats[home]['home_losses'] += 1
            team_stats[away]['away_wins'] += 1
        else:
            team_stats[home]['home_draws'] += 1
            team_stats[away]['away_draws'] += 1
    except:
        pass

print(f'Analyzed {len(team_stats)} teams')

# Calculate advanced metrics
print('\nCalculating advanced metrics...')
teams_data = {}

for team_key, stats in team_stats.items():
    if stats['total_matches'] < 5:
        continue
    
    total = stats['total_matches']
    home_m = stats['home_matches']
    away_m = stats['away_matches']
    
    # Overall stats
    total_wins = stats['home_wins'] + stats['away_wins']
    total_draws = stats['home_draws'] + stats['away_draws']
    total_goals_scored = stats['home_goals_scored'] + stats['away_goals_scored']
    total_goals_conceded = stats['home_goals_conceded'] + stats['away_goals_conceded']
    
    # Averages
    avg_goals_scored = total_goals_scored / total
    avg_goals_conceded = total_goals_conceded / total
    win_rate = total_wins / total
    
    # Home/Away split
    home_win_rate = stats['home_wins'] / home_m if home_m > 0 else 0
    away_win_rate = stats['away_wins'] / away_m if away_m > 0 else 0
    
    # Calculate metrics (0-100 scale)
    attack = min(100, max(0, avg_goals_scored * 35))
    defense = min(100, max(0, 100 - (avg_goals_conceded * 25)))
    form = min(100, max(0, (win_rate * 70) + ((total_draws / total) * 15)))
    
    # ELO rating
    elo = 1500 + ((win_rate - 0.5) * 400) + ((avg_goals_scored - avg_goals_conceded) * 50)
    elo = min(2500, max(1000, elo))
    
    # Home advantage
    home_advantage = (home_win_rate - away_win_rate) * 100
    
    teams_data[team_key] = {
        'attack': round(attack, 2),
        'defense': round(defense, 2),
        'form': round(form, 2),
        'elo': round(elo, 2),
        'matches': total,
        'wins': total_wins,
        'draws': total_draws,
        'losses': total - total_wins - total_draws,
        'goals_scored': total_goals_scored,
        'goals_conceded': total_goals_conceded,
        'home_advantage': round(home_advantage, 2),
        'avg_goals_scored': round(avg_goals_scored, 2),
        'avg_goals_conceded': round(avg_goals_conceded, 2)
    }

print(f'Calculated metrics for {len(teams_data)} teams')

# Save unified data
print('\nSaving unified data...')
with open('data/unified_matches.json', 'w', encoding='utf-8') as f:
    json.dump(all_matches, f, indent=2, ensure_ascii=False)
print(f'Saved {len(all_matches):,} matches to data/unified_matches.json')

with open('data/teams_advanced.json', 'w', encoding='utf-8') as f:
    json.dump(teams_data, f, indent=2, ensure_ascii=False)
print(f'Saved {len(teams_data)} teams to data/teams_advanced.json')

# Statistics
print('\n' + '=' * 60)
print('INTEGRATION SUMMARY')
print('=' * 60)
print(f'Total matches: {len(all_matches):,}')
print(f'Total teams: {len(teams_data)}')
print(f'\nTop 10 teams by ELO:')
top_teams = sorted(teams_data.items(), key=lambda x: x[1]['elo'], reverse=True)[:10]
for i, (team, data) in enumerate(top_teams, 1):
    print(f'  {i}. {team.title()}: ELO {data[\"elo\"]}, Attack {data[\"attack\"]}, Defense {data[\"defense\"]}')

print('\n✅ Integration completed successfully!')
