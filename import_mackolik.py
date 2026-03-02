import csv
import json
from datetime import datetime

def normalize_team(name):
    if not name:
        return ""
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

def parse_score(score_str):
    """Parse score like 1-2 to (1, 2)"""
    try:
        parts = score_str.split("-")
        return int(parts[0]), int(parts[1])
    except:
        return None, None

def import_mackolik_csv():
    print("=== Mackolik.csv Import ===")
    print()
    
    matches = []
    teams_stats = {}
    
    with open("mackolik.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        
        for row_num, row in enumerate(reader, 1):
            if row_num % 10000 == 0:
                print(f"Processing: {row_num} rows...")
            
            try:
                # Parse columns
                date_str = row[0]  # 01/01/2013
                season = row[1]    # 2012/2013
                time_str = row[2]  # 14:45
                code = row[3]      # 502
                league = row[4]    # İNP
                home = row[5]      # West Bromwich
                away = row[6]      # Fulham
                ht_score = row[7]  # 0-1 (Half Time)
                ft_score = row[8]  # 1-2 (Full Time)
                ms1 = row[9]       # Home odds
                msx = row[10]      # Draw odds
                ms2 = row[11]      # Away odds
                
                # Parse date
                try:
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    continue
                
                # Parse full time score
                home_score, away_score = parse_score(ft_score)
                if home_score is None or away_score is None:
                    continue
                
                # Parse odds
                try:
                    home_odds = float(ms1) if ms1 else None
                    draw_odds = float(msx) if msx else None
                    away_odds = float(ms2) if ms2 else None
                except:
                    home_odds = draw_odds = away_odds = None
                
                # Create match object
                match = {
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "season": season,
                    "league": league,
                    "home_team": home,
                    "away_team": away,
                    "home_score": home_score,
                    "away_score": away_score,
                    "odds": {
                        "1": home_odds,
                        "X": draw_odds,
                        "2": away_odds
                    }
                }
                
                matches.append(match)
                
                # Update team stats
                home_key = normalize_team(home)
                away_key = normalize_team(away)
                
                for team_key in [home_key, away_key]:
                    if team_key not in teams_stats:
                        teams_stats[team_key] = {
                            "scored": 0,
                            "conceded": 0,
                            "matches": 0,
                            "wins": 0,
                            "draws": 0
                        }
                
                # Home team stats
                teams_stats[home_key]["scored"] += home_score
                teams_stats[home_key]["conceded"] += away_score
                teams_stats[home_key]["matches"] += 1
                
                # Away team stats
                teams_stats[away_key]["scored"] += away_score
                teams_stats[away_key]["conceded"] += home_score
                teams_stats[away_key]["matches"] += 1
                
                # Win/Draw/Loss
                if home_score > away_score:
                    teams_stats[home_key]["wins"] += 1
                elif home_score < away_score:
                    teams_stats[away_key]["wins"] += 1
                else:
                    teams_stats[home_key]["draws"] += 1
                    teams_stats[away_key]["draws"] += 1
                
            except Exception as e:
                continue
    
    print(f"\nParsed {len(matches)} matches")
    print(f"Found {len(teams_stats)} teams")
    
    # Save matches
    with open("data/mackolik_matches.json", "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"Saved to data/mackolik_matches.json")
    
    # Calculate team metrics
    teams_data = {}
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
        
        teams_data[team_key] = {
            "attack": attack,
            "defense": defense,
            "form": form,
            "elo": elo,
            "matches": stats["matches"]
        }
    
    # Merge with existing teams
    try:
        with open("data/teams.json", "r", encoding="utf-8") as f:
            existing_teams = json.load(f)
        print(f"\nMerging with {len(existing_teams)} existing teams...")
        
        for team_key, new_data in teams_data.items():
            if team_key in existing_teams:
                old = existing_teams[team_key]
                # Weighted average: 50% old, 50% new (Mackolik has lots of data)
                existing_teams[team_key] = {
                    "attack": old["attack"] * 0.5 + new_data["attack"] * 0.5,
                    "defense": old["defense"] * 0.5 + new_data["defense"] * 0.5,
                    "form": old["form"] * 0.5 + new_data["form"] * 0.5,
                    "elo": old["elo"] * 0.5 + new_data["elo"] * 0.5,
                    "matches": old["matches"] + new_data["matches"]
                }
            else:
                existing_teams[team_key] = new_data
        
        teams_data = existing_teams
    except:
        print("\nNo existing teams, using new data")
    
    # Save teams
    with open("data/teams.json", "w", encoding="utf-8") as f:
        json.dump(teams_data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(teams_data)} teams to data/teams.json")
    
    # Statistics
    if matches:
        dates = [m["date"] for m in matches]
        leagues = set(m["league"] for m in matches)
        with_odds = sum(1 for m in matches if m["odds"]["1"])
        
        print(f"\n=== Statistics ===")
        print(f"Total matches: {len(matches)}")
        print(f"Date range: {min(dates)} to {max(dates)}")
        print(f"Leagues: {len(leagues)}")
        print(f"Matches with odds: {with_odds}")
        print(f"Teams: {len(teams_data)}")

if __name__ == "__main__":
    import_mackolik_csv()
