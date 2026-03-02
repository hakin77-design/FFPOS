import csv
import json
from datetime import datetime

print("=== Importing final_dataset.csv ===\n")

matches = []
teams_stats = {}

def normalize(name):
    if not name:
        return ""
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

with open("final_dataset.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        try:
            # Parse date
            date_str = row.get("Date", "")
            if not date_str:
                continue
            
            try:
                date_obj = datetime.strptime(date_str, "%d/%m/%y")
            except:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    continue
            
            home = row.get("HomeTeam", "")
            away = row.get("AwayTeam", "")
            fthg = row.get("FTHG", "")  # Full Time Home Goals
            ftag = row.get("FTAG", "")  # Full Time Away Goals
            
            if not all([home, away, fthg, ftag]):
                continue
            
            home_score = int(fthg)
            away_score = int(ftag)
            
            match = {
                "date": date_obj.strftime("%Y-%m-%d"),
                "league": "Premier League",
                "home_team": home,
                "away_team": away,
                "home_score": home_score,
                "away_score": away_score,
                "odds": {
                    "1": None,
                    "X": None,
                    "2": None
                }
            }
            
            matches.append(match)
            
            # Update team stats
            home_key = normalize(home)
            away_key = normalize(away)
            
            for team in [home_key, away_key]:
                if team not in teams_stats:
                    teams_stats[team] = {
                        "scored": 0,
                        "conceded": 0,
                        "matches": 0,
                        "wins": 0
                    }
            
            teams_stats[home_key]["scored"] += home_score
            teams_stats[home_key]["conceded"] += away_score
            teams_stats[home_key]["matches"] += 1
            
            teams_stats[away_key]["scored"] += away_score
            teams_stats[away_key]["conceded"] += home_score
            teams_stats[away_key]["matches"] += 1
            
            if home_score > away_score:
                teams_stats[home_key]["wins"] += 1
            elif home_score < away_score:
                teams_stats[away_key]["wins"] += 1
                
        except Exception as e:
            continue

print(f"Parsed {len(matches)} matches")
print(f"Found {len(teams_stats)} teams")

# Save matches
with open("data/final_dataset_matches.json", "w", encoding="utf-8") as f:
    json.dump(matches, f, indent=2, ensure_ascii=False)
print(f"Saved to data/final_dataset_matches.json")

# Update teams
with open("data/teams.json", "r", encoding="utf-8") as f:
    teams_data = json.load(f)

print(f"\nMerging with {len(teams_data)} existing teams...")

for team_key, stats in teams_stats.items():
    if stats["matches"] == 0:
        continue
    
    avg_scored = stats["scored"] / stats["matches"]
    avg_conceded = stats["conceded"] / stats["matches"]
    win_rate = stats["wins"] / stats["matches"]
    
    attack = min(100, max(0, avg_scored * 50))
    defense = min(100, max(0, 100 - (avg_conceded * 30)))
    form = min(100, max(0, win_rate * 100))
    elo = 1500 + (win_rate - 0.5) * 400
    
    if team_key in teams_data:
        old = teams_data[team_key]
        # Weighted: 70% old, 30% new
        teams_data[team_key] = {
            "attack": old["attack"] * 0.7 + attack * 0.3,
            "defense": old["defense"] * 0.7 + defense * 0.3,
            "form": old["form"] * 0.7 + form * 0.3,
            "elo": old["elo"] * 0.7 + elo * 0.3,
            "matches": old["matches"] + stats["matches"]
        }
    else:
        teams_data[team_key] = {
            "attack": attack,
            "defense": defense,
            "form": form,
            "elo": elo,
            "matches": stats["matches"]
        }

with open("data/teams.json", "w", encoding="utf-8") as f:
    json.dump(teams_data, f, indent=2, ensure_ascii=False)

print(f"Updated teams.json with {len(teams_data)} teams")

if matches:
    dates = [m["date"] for m in matches]
    print(f"\n=== Statistics ===")
    print(f"Total matches: {len(matches)}")
    print(f"Date range: {min(dates)} to {max(dates)}")
    print(f"Teams: {len(teams_stats)}")

print("\n✅ final_dataset.csv imported successfully!")
