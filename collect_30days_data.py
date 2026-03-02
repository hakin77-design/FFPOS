import requests
import json
from datetime import datetime, timedelta
import time

API_KEY = "26d3b5add4msh11d7911c21ce945p14a3a4jsna48caf83e346"
API_HOST = "flashscore4.p.rapidapi.com"

def fetch_matches_by_date(date_str):
    url = "https://flashscore4.p.rapidapi.com/api/flashscore/v2/matches/list-by-date"
    
    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": API_KEY
    }
    
    params = {
        "sport_id": "1",
        "date": date_str,
        "timezone": "Europe/Berlin"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict) and data.get("error"):
            return []
        
        matches = []
        for item in data:
            try:
                home = item.get("home_team", {}).get("name", "")
                away = item.get("away_team", {}).get("name", "")
                home_score = item.get("home_score")
                away_score = item.get("away_score")
                
                if not all([home, away]) or home_score is None or away_score is None:
                    continue
                
                match = {
                    "date": date_str,
                    "league": item.get("league", {}).get("name", "Unknown"),
                    "home_team": home,
                    "away_team": away,
                    "home_score": int(home_score),
                    "away_score": int(away_score),
                    "odds": {
                        "1": item.get("odds", {}).get("1"),
                        "X": item.get("odds", {}).get("X"),
                        "2": item.get("odds", {}).get("2")
                    }
                }
                matches.append(match)
            except:
                continue
        
        return matches
    except Exception as e:
        print(f"  Error {date_str}: {e}")
        return []

def normalize_team(name):
    if not name:
        return ""
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

def update_teams(matches, teams_data):
    stats = {}
    
    for m in matches:
        home = normalize_team(m["home_team"])
        away = normalize_team(m["away_team"])
        hs = m["home_score"]
        as_ = m["away_score"]
        
        for team in [home, away]:
            if team not in stats:
                stats[team] = {"scored": 0, "conceded": 0, "matches": 0, "wins": 0}
        
        stats[home]["scored"] += hs
        stats[home]["conceded"] += as_
        stats[home]["matches"] += 1
        
        stats[away]["scored"] += as_
        stats[away]["conceded"] += hs
        stats[away]["matches"] += 1
        
        if hs > as_:
            stats[home]["wins"] += 1
        elif hs < as_:
            stats[away]["wins"] += 1
    
    for team, s in stats.items():
        if s["matches"] == 0:
            continue
        
        avg_scored = s["scored"] / s["matches"]
        avg_conceded = s["conceded"] / s["matches"]
        win_rate = s["wins"] / s["matches"]
        
        attack = min(100, max(0, avg_scored * 50))
        defense = min(100, max(0, 100 - (avg_conceded * 30)))
        form = min(100, max(0, win_rate * 100))
        elo = 1500 + (win_rate - 0.5) * 400
        
        if team in teams_data:
            old = teams_data[team]
            teams_data[team] = {
                "attack": old["attack"] * 0.7 + attack * 0.3,
                "defense": old["defense"] * 0.7 + defense * 0.3,
                "form": old["form"] * 0.7 + form * 0.3,
                "elo": old["elo"] * 0.7 + elo * 0.3,
                "matches": old["matches"] + s["matches"]
            }
        else:
            teams_data[team] = {
                "attack": attack,
                "defense": defense,
                "form": form,
                "elo": elo,
                "matches": s["matches"]
            }
    
    return teams_data

def main():
    print("=== RapidAPI Flashscore - 30 Gün Geçmiş Veri ===")
    print()
    
    # Son 30 gün
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    all_matches = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"{date_str}...", end=" ")
        
        matches = fetch_matches_by_date(date_str)
        all_matches.extend(matches)
        
        print(f"{len(matches)} maç")
        
        current_date += timedelta(days=1)
        time.sleep(0.5)  # Rate limiting
    
    print(f"\nToplam: {len(all_matches)} maç")
    
    # Mevcut verilerle birleştir
    try:
        with open("data/historical_matches.json") as f:
            existing = json.load(f)
        print(f"Mevcut: {len(existing)} maç")
        
        # Tarihe göre birleştir
        all_data = existing + all_matches
        print(f"Birleştirilmiş: {len(all_data)} maç")
    except:
        all_data = all_matches
    
    # Kaydet
    with open("data/historical_matches.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"Kaydedildi: data/historical_matches.json")
    
    # Takımları güncelle
    try:
        with open("data/teams.json") as f:
            teams_data = json.load(f)
    except:
        teams_data = {}
    
    print(f"\nTakımlar güncelleniyor...")
    teams_data = update_teams(all_matches, teams_data)
    
    with open("data/teams.json", "w", encoding="utf-8") as f:
        json.dump(teams_data, f, indent=2, ensure_ascii=False)
    print(f"Kaydedildi: {len(teams_data)} takım")

if __name__ == "__main__":
    main()
