import csv, json, os
from datetime import datetime
from collections import defaultdict

print('FFPAS DATA-RAW IMPORT')
DATA_RAW_DIR, OUTPUT_DIR = 'data-raw', 'data'
all_matches, teams_stats, matches_by_league = [], {}, defaultdict(int)

def normalize(name):
    return name.lower().strip() if name else ''

def parse_date(s):
    if not s: return None
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%m/%d/%Y']:
        try: return datetime.strptime(s, fmt)
        except: pass
    return None

def get_league(fn):
    leagues = {'england':'Premier League','spain':'La Liga','germany':'Bundesliga','italy':'Serie A','france':'Ligue 1','turkey':'Süper Lig','holland':'Eredivisie','portugal':'Primeira Liga','belgium':'Pro League','greece':'Super League','scotland':'Scottish Premiership','champs':'Champions League','facup':'FA Cup','leaguecup':'League Cup'}
    for k, v in leagues.items():
        if k in fn.lower(): return v
    return fn.replace('.csv', '').replace('_', ' ').title()

print(f'Scanning {DATA_RAW_DIR}...')
csv_files = sorted([f for f in os.listdir(DATA_RAW_DIR) if f.endswith('.csv')])
print(f'Found {len(csv_files)} CSV files')

for fn in csv_files:
    league = get_league(fn)
    print(f'Processing: {fn} ({league})')
    count = 0
    try:
        with open(os.path.join(DATA_RAW_DIR, fn), 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    d = parse_date(row.get('Date') or row.get('date'))
                    if not d: continue
                    h = row.get('home') or row.get('HomeTeam') or row.get('Home')
                    a = row.get('visitor') or row.get('AwayTeam') or row.get('Away') or row.get('away')
                    if not h or not a: continue
                    hs = as_ = None
                    if 'hgoal' in row and 'vgoal' in row:
                        hs, as_ = int(row['hgoal']), int(row['vgoal'])
                    elif 'FTHG' in row and 'FTAG' in row:
                        hs, as_ = int(row['FTHG']), int(row['FTAG'])
                    if hs is None or as_ is None: continue
                    all_matches.append({'date':d.strftime('%Y-%m-%d'),'league':league,'home_team':h.strip(),'away_team':a.strip(),'home_score':hs,'away_score':as_})
                    for team, scored, conceded in [(normalize(h), hs, as_), (normalize(a), as_, hs)]:
                        if team not in teams_stats:
                            teams_stats[team] = {'name': h if team == normalize(h) else a, 'scored': 0, 'conceded': 0, 'matches': 0, 'wins': 0}
                        teams_stats[team]['scored'] += scored
                        teams_stats[team]['conceded'] += conceded
                        teams_stats[team]['matches'] += 1
                        if scored > conceded: teams_stats[team]['wins'] += 1
                    matches_by_league[league] += 1
                    count += 1
                except: pass
        print(f'  Imported {count} matches')
    except Exception as e: print(f'  Error: {e}')

print(f'Total: {len(all_matches)} matches, {len(teams_stats)} teams')
if all_matches:
    dates = [m['date'] for m in all_matches]
    print(f'Date range: {min(dates)} to {max(dates)}')

print('Top 10 Leagues:')
for league, count in sorted(matches_by_league.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f'  {league}: {count}')

os.makedirs(OUTPUT_DIR, exist_ok=True)
matches_file = os.path.join(OUTPUT_DIR, 'data_raw_matches.json')
with open(matches_file, 'w', encoding='utf-8') as f:
    json.dump(all_matches, f, indent=2, ensure_ascii=False)
print(f'Saved {len(all_matches)} matches to {matches_file}')

teams_data = {}
teams_file = os.path.join(OUTPUT_DIR, 'teams.json')
try:
    with open(teams_file, 'r', encoding='utf-8') as f:
        teams_data = json.load(f)
    print(f'Loaded {len(teams_data)} existing teams')
except: print('No existing teams file')

for tk, st in teams_stats.items():
    if st['matches'] > 0:
        avg_scored = st['scored'] / st['matches']
        avg_conceded = st['conceded'] / st['matches']
        win_rate = st['wins'] / st['matches']
        new_metrics = {'name': st['name'], 'attack': min(100, max(0, avg_scored * 35)), 'defense': min(100, max(0, 100 - avg_conceded * 25)), 'form': min(100, max(0, win_rate * 100)), 'elo': max(1000, min(2500, 1500 + (win_rate - 0.5) * 400)), 'matches': st['matches']}
        if tk in teams_data:
            old = teams_data[tk]
            teams_data[tk] = {'name': new_metrics['name'], 'attack': round(old.get('attack', 50) * 0.6 + new_metrics['attack'] * 0.4, 2), 'defense': round(old.get('defense', 50) * 0.6 + new_metrics['defense'] * 0.4, 2), 'form': round(old.get('form', 50) * 0.6 + new_metrics['form'] * 0.4, 2), 'elo': round(old.get('elo', 1500) * 0.6 + new_metrics['elo'] * 0.4, 2), 'matches': old.get('matches', 0) + new_metrics['matches']}
        else:
            teams_data[tk] = {k: round(v, 2) if isinstance(v, float) else v for k, v in new_metrics.items()}

with open(teams_file, 'w', encoding='utf-8') as f:
    json.dump(teams_data, f, indent=2, ensure_ascii=False)
print(f'Saved {len(teams_data)} teams to {teams_file}')
print('Done!')
