import sqlite3
import json
from collections import defaultdict

print('Reading European database...')
conn = sqlite3.connect('european_database.sqlite')
cursor = conn.cursor()

# Get all divisions
cursor.execute('SELECT * FROM divisions')
divisions = {row[0]: {'name': row[1], 'country': row[2]} for row in cursor.fetchall()}
print(f'Found {len(divisions)} divisions')

# Get all matches
cursor.execute('''
    SELECT Div, Date, HomeTeam, AwayTeam, FTHG, FTAG, FTR, season 
    FROM matchs 
    WHERE FTHG IS NOT NULL AND FTAG IS NOT NULL
    ORDER BY Date
''')

matches = []
teams_set = set()

for row in cursor.fetchall():
    div, date, home, away, fthg, ftag, ftr, season = row
    
    if div in divisions:
        league_name = f"{divisions[div]['name']} ({divisions[div]['country']})"
    else:
        league_name = div
    
    match = {
        'date': date,
        'league': league_name,
        'home': home,
        'away': away,
        'home_goals': int(fthg),
        'away_goals': int(ftag),
        'result': ftr,  # H=Home, A=Away, D=Draw
        'season': season
    }
    matches.append(match)
    teams_set.add(home)
    teams_set.add(away)

conn.close()

print(f'Loaded {len(matches)} matches')
print(f'Found {len(teams_set)} unique teams')

# Save to JSON
output_file = 'data/european_matches.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print(f'Saved to {output_file}')

# Show statistics
print('\n=== STATISTICS ===')
print(f'Date range: {matches[0]["date"]} to {matches[-1]["date"]}')

# Count by league
league_counts = defaultdict(int)
for m in matches:
    league_counts[m['league']] += 1

print('\nTop 10 leagues by match count:')
for league, count in sorted(league_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f'  {league}: {count} matches')
