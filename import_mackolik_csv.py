import csv
import json
from datetime import datetime

def normalize_team(name):
    if not name:
        return ""
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

def parse_mackolik_csv():
    print("=== Mackolik CSV Import ===")
    print()
    
    matches = []
    errors = 0
    
    with open("mackolik.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        
        for i, row in enumerate(reader, 1):
            if i % 10000 == 0:
                print(f"İşlenen: {i} satır...")
            
            try:
                if len(row) < 12:
                    continue
                
                # Parse fields
                date_str = row[0]  # 01/01/2013
                season = row[1]    # 2012/2013
                time_str = row[2]  # 14:45
                match_id = row[3]  # 502
                league = row[4]    # İNP (Premier League)
                home_team = row[5] # West Bromwich
                away_team = row[6] # Fulham
                ht_score = row[7]  # 0-1 (Half time)
                ft_score = row[8]  # 1-2 (Full time)
                
                # Odds (columns 9-11)
                home_odds = row[9] if len(row) > 9 and row[9] else None
                draw_odds = row[10] if len(row) > 10 and row[10] else None
                away_odds = row[11] if len(row) > 11 and row[11] else None
                
                # Parse date
                try:
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    continue
                
                # Parse full time score
                if not ft_score or "-" not in ft_score:
                    continue
                
                score_parts = ft_score.split("-")
                if len(score_parts) != 2:
                    continue
                
                home_score = int(score_parts[0])
                away_score = int(score_parts[1])
                
                # League mapping
                league_map = {
                    "İNP": "Premier League",
                    "İNCL": "Championship",
                    "İN1": "League One",
                    "İN2": "League Two",
                    "İSL": "La Liga",
                    "İSL2": "La Liga 2",
                    "İTA": "Serie A",
                    "İTB": "Serie B",
                    "İBL": "Bundesliga",
                    "İBL2": "Bundesliga 2",
                    "İFL": "Ligue 1",
                    "İFL2": "Ligue 2",
                    "İNL": "Eredivisie",
                    "İPL": "Liga Portugal",
                    "İTSL": "Super Lig",
                    "İGSL": "Super League"
                }
                
                league_name = league_map.get(league, league)
                
                match = {
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "season": season,
                    "league": league_name,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "odds": {
                        "1": float(home_odds) if home_odds else None,
                        "X": float(draw_odds) if draw_odds else None,
                        "2": float(away_odds) if away_odds else None
                    }
                }
                
                matches.append(match)
                
            except Exception as e:
                errors += 1
                if errors < 10:
                    print(f"Hata satır {i}: {e}")
                continue
    
    print(f"\nToplam: {len(matches)} maç parse edildi")
    print(f"Hatalar: {errors}")
    
    return matches

def update_teams(matches, teams_data):
    print(f"\nTakımlar güncelleniyor...")
    
    stats = {}
    
    for m in matches:
        home = normalize_team(m["home_team"])
        away = normalize_team(m["away_team"])
        hs = m["home_score"]
        as_ = m["away_score"]
        
        for team in [home, away]:
            if team not in stats:
                stats[team] = {"scored": 0, "conceded": 0, "matches": 0, "wins": 0, "draws": 0}
        
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
        else:
            stats[home]["draws"] += 1
            stats[away]["draws"] += 1
    
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
            # Mackolik data is historical, give it 50% weight
            teams_data[team] = {
                "attack": old["attack"] * 0.5 + attack * 0.5,
                "defense": old["defense"] * 0.5 + defense * 0.5,
                "form": old["form"] * 0.5 + form * 0.5,
                "elo": old["elo"] * 0.5 + elo * 0.5,
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
    
    print(f"Güncellenen takım: {len(stats)}")
    return teams_data

def main():
    # Parse CSV
    matches = parse_mackolik_csv()
    
    if not matches:
        print("Hiç maç bulunamadı!")
        return
    
    # Date range
    dates = [m["date"] for m in matches]
    print(f"Tarih aralığı: {min(dates)} - {max(dates)}")
    
    # Leagues
    leagues = set(m["league"] for m in matches)
    print(f"Ligler: {len(leagues)}")
    for league in sorted(leagues):
        count = sum(1 for m in matches if m["league"] == league)
        print(f"  {league}: {count} maç")
    
    # Save matches
    output_file = "data/mackolik_matches.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"\nKaydedildi: {output_file}")
    
    # Load existing teams
    try:
        with open("data/teams.json") as f:
            teams_data = json.load(f)
        print(f"\nMevcut takımlar: {len(teams_data)}")
    except:
        teams_data = {}
        print("\nYeni takım veritabanı oluşturuluyor")
    
    # Update teams
    teams_data = update_teams(matches, teams_data)
    
    # Save teams
    with open("data/teams.json", "w", encoding="utf-8") as f:
        json.dump(teams_data, f, indent=2, ensure_ascii=False)
    print(f"Takımlar kaydedildi: {len(teams_data)} takım")
    
    # Merge with historical data
    try:
        with open("data/historical_matches.json") as f:
            existing = json.load(f)
        print(f"\nMevcut geçmiş veri: {len(existing)} maç")
        
        all_matches = existing + matches
        
        with open("data/historical_matches.json", "w", encoding="utf-8") as f:
            json.dump(all_matches, f, indent=2, ensure_ascii=False)
        
        print(f"Birleştirilmiş toplam: {len(all_matches)} maç")
    except:
        print("\nGeçmiş veri dosyası bulunamadı, sadece Mackolik verisi kaydedildi")
    
    # Stats
    with_odds = sum(1 for m in matches if m["odds"]["1"])
    print(f"\n=== İstatistikler ===")
    print(f"Toplam maç: {len(matches)}")
    print(f"Oranları olan: {with_odds}")
    print(f"Takımlar: {len(teams_data)}")

if __name__ == "__main__":
    main()
