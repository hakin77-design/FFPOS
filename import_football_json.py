import json
import os
from collections import defaultdict
from pathlib import Path

print('=== SCANNING FOOTBALL.JSON-MASTER ===\n')

base_path = 'football.json-master'
all_matches = []
league_counts = defaultdict(int)
season_counts = defaultdict(int)
errors = []

# Scan all JSON files
json_files = list(Path(base_path).rglob('*.json'))
print(f'Found {len(json_files)} JSON files')

for json_file in json_files:
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'matches' in data and isinstance(data['matches'], list):
            league_name = data.get('name', 'Unknown League')
            season = str(json_file.parent.name)
            
            for match in data['matches']:
                # Extract match data
                if 'score' in match and 'ft' in match['score']:
                    ft_score = match['score']['ft']
                    
                    match_data = {
                        'date': match.get('date', ''),
                        'league': league_name,
                        'season': season,
                        'home': match.get('team1', ''),
                        'away': match.get('team2', ''),
                        'home_goals': ft_score[0] if len(ft_score) > 0 else 0,
                        'away_goals': ft_score[1] if len(ft_score) > 1 else 0,
                        'round': match.get('round', '')
                    }
                    
                    # Determine result
                    if match_data['home_goals'] > match_data['away_goals']:
                        match_data['result'] = 'H'
                    elif match_data['home_goals'] < match_data['away_goals']:
                        match_data['result'] = 'A'
                    else:
                        match_data['result'] = 'D'
                    
                    all_matches.append(match_data)
                    league_counts[league_name] += 1
                    season_counts[season] += 1
    
    except Exception as e:
        errors.append(f'{json_file}: {str(e)}')

print(f'\n=== RESULTS ===')
print(f'Total matches extracted: {len(all_matches)}')
print(f'Unique leagues: {len(league_counts)}')
print(f'Seasons covered: {len(season_counts)}')

if errors:
    print(f'\nErrors: {len(errors)}')
    for err in errors[:5]:
        print(f'  - {err}')

# Save to JSON
output_file = 'data/football_json_matches.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_matches, f, ensure_ascii=False, indent=2)

print(f'\n✓ Saved to {output_file}')

# Show statistics
print('\n=== TOP 10 LEAGUES ===')
for league, count in sorted(league_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f'{league}: {count} matches')

print('\n=== SEASONS ===')
for season in sorted(season_counts.keys()):
    print(f'{season}: {season_counts[season]} matches')
