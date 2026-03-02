import json

print("=== Fixing Team Statistics ===\n")

# Load teams
with open("data/teams.json") as f:
    teams = json.load(f)

print(f"Total teams: {len(teams)}")

# Find problematic teams
problems = []
for key, stats in teams.items():
    attack = stats.get("attack", 0)
    defense = stats.get("defense", 0)
    form = stats.get("form", 0)
    elo = stats.get("elo", 1500)
    
    # Check for abnormal values
    if attack < 10 or defense < 10 or form < 10:
        problems.append((key, stats))

print(f"Found {len(problems)} teams with low stats\n")

# Recalculate from match data
print("Recalculating from Mackolik data...")

with open("data/mackolik_matches.json") as f:
    matches = json.load(f)

def normalize(name):
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

team_stats = {}

for match in matches:
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
                "draws": 0
            }
    
    team_stats[home]["scored"] += hs
    team_stats[home]["conceded"] += as_
    team_stats[home]["matches"] += 1
    
    team_stats[away]["scored"] += as_
    team_stats[away]["conceded"] += hs
    team_stats[away]["matches"] += 1
    
    if hs > as_:
        team_stats[home]["wins"] += 1
    elif hs < as_:
        team_stats[away]["wins"] += 1
    else:
        team_stats[home]["draws"] += 1
        team_stats[away]["draws"] += 1

# Update teams with proper calculations
updated = 0
for team_key, stats in team_stats.items():
    if stats["matches"] < 5:  # Skip teams with too few matches
        continue
    
    avg_scored = stats["scored"] / stats["matches"]
    avg_conceded = stats["conceded"] / stats["matches"]
    win_rate = stats["wins"] / stats["matches"]
    
    # Proper scaling
    attack = min(100, max(0, avg_scored * 50))
    defense = min(100, max(0, 100 - (avg_conceded * 30)))
    form = min(100, max(0, win_rate * 100))
    elo = 1500 + (win_rate - 0.5) * 400
    
    # Only update if values are reasonable
    if attack >= 10 and defense >= 10:
        teams[team_key] = {
            "attack": attack,
            "defense": defense,
            "form": form,
            "elo": elo,
            "matches": stats["matches"]
        }
        updated += 1

print(f"Updated {updated} teams")

# Save
with open("data/teams.json", "w", encoding="utf-8") as f:
    json.dump(teams, f, indent=2, ensure_ascii=False)

print(f"Saved to data/teams.json")

# Verify key teams
print("\n=== Verification ===")
test_teams = ["manchestercity", "barcelona", "realmadrid", "bayernmunich", "liverpool"]
for key in test_teams:
    if key in teams:
        t = teams[key]
        print(f"{key}: Attack={t[\"attack\"]:.0f}, Defense={t[\"defense\"]:.0f}, ELO={t[\"elo\"]:.0f}")

print("\n✅ Team stats fixed!")
