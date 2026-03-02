import json
import unicodedata
from collections import defaultdict

def normalize(name):
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    name = name.lower().replace(' ', '').replace('-', '').replace('.', '').replace("'", '')
    return name

print('Loading existing teams...')
with open('data/teams.json', 'r', encoding='utf-8') as f:
    teams = json.load(f)

print(f'Current teams: {len(teams)}')

print('\nLoading European matches...')
with open('data/european_matches.json', 'r', encoding='utf-8') as f:
    european_matches = json.load(f)

print(f'European matches: {len(european_matches)}')

# Calculate team statistics from European data
team_stats = defaultdict(lambda: {
    'goals_scored': 0,
    'goals_conceded': 0,
    'wins': 0,
    'draws': 0,
    'losses': 0,
    'matches': 0
})

for match in european_matches:
    home = normalize(match['home'])
    away = normalize(match['away'])
    home_goals = match['home_goals']
    away_goals = match['away_goals']
    
    # Home team stats
    team_stats[home]['goals_scored'] += home_goals
    team_stats[home]['goals_conceded'] += away_goals
    team_stats[home]['matches'] += 1
    
    # Away team stats
    team_stats[away]['goals_scored'] += away_goals
    team_stats[away]['goals_conceded'] += home_goals
    team_stats[away]['matches'] += 1
    
    # Results
    if home_goals > away_goals:
        team_stats[home]['wins'] += 1
        team_stats[away]['losses'] += 1
    elif home_goals < away_goals:
        team_stats[away]['wins'] += 1
        team_stats[home]['losses'] += 1
    else:
        team_stats[home]['draws'] += 1
        team_stats[away]['draws'] += 1

# Merge with existing teams
new_teams = 0
updated_teams = 0

for team_name, stats in team_stats.items():
    if stats['matches'] < 10:  # Skip teams with too few matches
        continue
    
    # Calculate metrics
    attack = (stats['goals_scored'] / stats['matches']) * 20  # Scale to 0-100
    defense = 100 - ((stats['goals_conceded'] / stats['matches']) * 20)  # Inverse
    win_rate = (stats['wins'] / stats['matches']) * 100
    form = win_rate * 0.7 + (stats['draws'] / stats['matches']) * 30
    
    # ELO calculation
    elo = 1500 + (win_rate - 50) * 10
    
    if team_name in teams:
        # Merge: average with existing data
        old = teams[team_name]
        old_weight = old['matches'] / (old['matches'] + stats['matches'])
        new_weight = stats['matches'] / (old['matches'] + stats['matches'])
        
        teams[team_name] = {
            'attack': round(old['attack'] * old_weight + attack * new_weight, 2),
            'defense': round(old['defense'] * old_weight + defense * new_weight, 2),
            'form': round(old['form'] * old_weight + form * new_weight, 2),
            'elo': round(old['elo'] * old_weight + elo * new_weight, 2),
            'matches': old['matches'] + stats['matches']
        }
        updated_teams += 1
    else:
        teams[team_name] = {
            'attack': round(attack, 2),
            'defense': round(defense, 2),
            'form': round(form, 2),
            'elo': round(elo, 2),
            'matches': stats['matches']
        }
        new_teams += 1

print(f'\n=== MERGE RESULTS ===')
print(f'New teams added: {new_teams}')
print(f'Existing teams updated: {updated_teams}')
print(f'Total teams: {len(teams)}')

# Save merged data
with open('data/teams.json', 'w', encoding='utf-8') as f:
    json.dump(teams, f, ensure_ascii=False, indent=2)

print('\nSaved to data/teams.json')

# Show some examples
print('\n=== SAMPLE TEAMS ===')
sample_teams = ['manchesterunited', 'barcelona', 'realmadrid', 'bayernmunchen', 'liverpool']
for team in sample_teams:
    if team in teams:
        t = teams[team]
        print(f'{team}: Attack={t["attack"]:.1f}, Defense={t["defense"]:.1f}, ELO={t["elo"]:.0f}, Matches={t["matches"]}')
