import json
from collections import defaultdict

print("=== Data Cleaning & Fixing ===\n")

# Load all match data
print("Loading data...")
with open("data/mackolik_matches.json") as f:
    mackolik = json.load(f)
print(f"Mackolik: {len(mackolik):,} matches")

with open("data/historical_matches.json") as f:
    historical = json.load(f)
print(f"Historical: {len(historical):,} matches")

with open("data/final_dataset_matches.json") as f:
    final_ds = json.load(f)
print(f"Final Dataset: {len(final_ds):,} matches")

all_matches = mackolik + historical + final_ds
print(f"Total before cleaning: {len(all_matches):,} matches\n")

# Check for duplicates
print("Checking for duplicates...")
seen = set()
duplicates = []
unique_matches = []

for match in all_matches:
    # Create unique key: date + home + away + score
    key = (
        match["date"],
        match["home_team"].lower().strip(),
        match["away_team"].lower().strip(),
        match["home_score"],
        match["away_score"]
    )
    
    if key in seen:
        duplicates.append(match)
    else:
        seen.add(key)
        unique_matches.append(match)

print(f"Found {len(duplicates):,} duplicate matches")
print(f"Unique matches: {len(unique_matches):,}\n")

# Show some duplicate examples
if duplicates:
    print("Sample duplicates:")
    dup_count = defaultdict(int)
    for match in all_matches:
        key = (match["date"], match["home_team"], match["away_team"])
        dup_count[key] += 1
    
    shown = 0
    for key, count in sorted(dup_count.items(), key=lambda x: -x[1]):
        if count > 1 and shown < 5:
            print(f"  {key[0]} {key[1]} vs {key[2]}: {count} times")
            shown += 1
    print()

# Save cleaned data
print("Saving cleaned data...")
with open("data/mackolik_matches.json", "w", encoding="utf-8") as f:
    json.dump([m for m in unique_matches if m in mackolik], f, indent=2, ensure_ascii=False)

with open("data/historical_matches.json", "w", encoding="utf-8") as f:
    json.dump([m for m in unique_matches if m in historical], f, indent=2, ensure_ascii=False)

with open("data/final_dataset_matches.json", "w", encoding="utf-8") as f:
    json.dump([m for m in unique_matches if m in final_ds], f, indent=2, ensure_ascii=False)

print(f"Cleaned data saved\n")

# Recalculate team statistics from scratch
print("Recalculating team statistics from scratch...")

def normalize(name):
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

team_stats = {}

for match in unique_matches:
    home = normalize(match["home_team"])
    away = normalize(match["away_team"])
    hs = match["home_score"]
    as_ = match["away_score"]
    
    for team in [home, away]:
        if team not in team_stats:
            team_stats[team] = {
                "scored": 0,
                "conceded": 0,
                "matches": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0
            }
    
    # Home team
    team_stats[home]["scored"] += hs
    team_stats[home]["conceded"] += as_
    team_stats[home]["matches"] += 1
    
    # Away team
    team_stats[away]["scored"] += as_
    team_stats[away]["conceded"] += hs
    team_stats[away]["matches"] += 1
    
    # Results
    if hs > as_:
        team_stats[home]["wins"] += 1
        team_stats[away]["losses"] += 1
    elif hs < as_:
        team_stats[away]["wins"] += 1
        team_stats[home]["losses"] += 1
    else:
        team_stats[home]["draws"] += 1
        team_stats[away]["draws"] += 1

# Calculate proper statistics
teams_data = {}
for team_key, stats in team_stats.items():
    if stats["matches"] < 3:  # Skip teams with too few matches
        continue
    
    matches = stats["matches"]
    avg_scored = stats["scored"] / matches
    avg_conceded = stats["conceded"] / matches
    win_rate = stats["wins"] / matches
    draw_rate = stats["draws"] / matches
    
    # Proper scaling (0-100)
    attack = min(100, max(10, avg_scored * 50))
    defense = min(100, max(10, 100 - (avg_conceded * 30)))
    form = min(100, max(10, win_rate * 100))
    
    # ELO calculation
    elo = 1500 + (win_rate - 0.5) * 400
    elo = max(1100, min(1900, elo))  # Constrain to reasonable range
    
    teams_data[team_key] = {
        "attack": round(attack, 2),
        "defense": round(defense, 2),
        "form": round(form, 2),
        "elo": round(elo, 2),
        "matches": matches
    }

print(f"Calculated stats for {len(teams_data):,} teams")

# Save teams
with open("data/teams.json", "w", encoding="utf-8") as f:
    json.dump(teams_data, f, indent=2, ensure_ascii=False)

print(f"Saved to data/teams.json\n")

# Verify some teams
print("=== Sample Team Stats ===")
test_teams = ["manchestercity", "barcelona", "realmadrid", "liverpool", "bayernmunich"]
for key in test_teams:
    if key in teams_data:
        t = teams_data[key]
        print(f"{key:20s} Attack:{t[
