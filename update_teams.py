#!/usr/bin/env python3
"""
Takım istatistiklerini RapidAPI'den gelen maçlarla günceller
"""
import json
import os
from ai.scrapers.rapidapi_scraper import get_live_matches
from ai.models.team_engine import normalize

def update_team_stats():
    # Mevcut takım verilerini yükle
    teams_file = os.path.join(os.path.dirname(__file__), 'data/teams.json')
    
    try:
        with open(teams_file, 'r', encoding='utf-8') as f:
            teams = json.load(f)
    except:
        teams = {}
    
    # RapidAPI'den maçları çek
    matches = get_live_matches()
    
    print(f"Updating stats from {len(matches)} matches...")
    
    updated_count = 0
    new_teams = 0
    
    for match in matches:
        home_name = match['home']
        away_name = match['away']
        
        # Takım isimlerini normalize et
        home_key = normalize(home_name)
        away_key = normalize(away_name)
        
        # Yeni takımları ekle
        if home_key not in teams:
            teams[home_key] = {
                "attack": 1.0,
                "defense": 1.0,
                "form": 0.5,
                "elo": 1500,
                "matches": 0
            }
            new_teams += 1
            print(f"  + New team: {home_name}")
        
        if away_key not in teams:
            teams[away_key] = {
                "attack": 1.0,
                "defense": 1.0,
                "form": 0.5,
                "elo": 1500,
                "matches": 0
            }
            new_teams += 1
            print(f"  + New team: {away_name}")
        
        # Maç sayısını artır
        teams[home_key]["matches"] = teams[home_key].get("matches", 0) + 1
        teams[away_key]["matches"] = teams[away_key].get("matches", 0) + 1
        
        updated_count += 1
    
    # Güncellenmiş verileri kaydet
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    
    print(f"\nStats updated!")
    print(f"  - Total teams: {len(teams)}")
    print(f"  - New teams added: {new_teams}")
    print(f"  - Matches processed: {updated_count}")
    
    return teams

if __name__ == "__main__":
    update_team_stats()
