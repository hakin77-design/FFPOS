#!/usr/bin/env python3
"""
Geçmiş maç verilerini çeker ve modeli eğitir
Football-Data.org'dan ücretsiz geçmiş maç verileri
"""
import requests
import pandas as pd
import json
import os
from datetime import datetime

def download_historical_data(start_year=2010, end_year=2026):
    """
    Football-Data.org'dan geçmiş maç verilerini indir
    """
    base_url = "https://www.football-data.co.uk/mmz4281"
    
    # Desteklenen ligler
    leagues = {
        'E0': 'Premier League',
        'E1': 'Championship',
        'SP1': 'La Liga',
        'D1': 'Bundesliga',
        'I1': 'Serie A',
        'F1': 'Ligue 1',
        'N1': 'Eredivisie',
        'P1': 'Primeira Liga',
        'T1': 'Super Lig',
        'G1': 'Super League Greece'
    }
    
    all_matches = []
    
    print(f"Downloading historical data from {start_year} to {end_year}...")
    
    for year in range(start_year, end_year):
        season = f"{str(year)[2:]}{str(year+1)[2:]}"
        
        for league_code, league_name in leagues.items():
            url = f"{base_url}/{season}/{league_code}.csv"
            
            try:
                print(f"  Fetching {league_name} {year}/{year+1}...")
                df = pd.read_csv(url, encoding='latin1')
                
                # Sadece gerekli kolonları al
                required_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H', 'B365D', 'B365A']
                
                if all(col in df.columns for col in required_cols):
                    df = df[required_cols].copy()
                    df['League'] = league_name
                    df['Season'] = f"{year}/{year+1}"
                    
                    # NaN değerleri temizle
                    df = df.dropna(subset=['B365H', 'B365D', 'B365A'])
                    
                    all_matches.append(df)
                    print(f"    ✓ {len(df)} matches")
                else:
                    print(f"    ✗ Missing columns")
                    
            except Exception as e:
                print(f"    ✗ Error: {str(e)[:50]}")
    
    if not all_matches:
        print("\nNo data downloaded!")
        return None
    
    # Tüm verileri birleştir
    combined_df = pd.concat(all_matches, ignore_index=True)
    
    print(f"\nTotal matches downloaded: {len(combined_df)}")
    
    # Veriyi kaydet
    output_file = 'data/historical_matches.csv'
    os.makedirs('data', exist_ok=True)
    combined_df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")
    
    return combined_df

def prepare_training_data(df):
    """
    Eğitim verisi hazırla
    """
    print("\nPreparing training data...")
    
    training_data = []
    
    for _, row in df.iterrows():
        match_data = {
            'home_team': row['HomeTeam'],
            'away_team': row['AwayTeam'],
            'home_goals': int(row['FTHG']),
            'away_goals': int(row['FTAG']),
            'result': row['FTR'],  # H, D, A
            'odds_home': float(row['B365H']),
            'odds_draw': float(row['B365D']),
            'odds_away': float(row['B365A']),
            'league': row['League'],
            'season': row['Season'],
            'date': row['Date']
        }
        training_data.append(match_data)
    
    # JSON olarak kaydet
    output_file = 'data/training_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    print(f"Training data saved: {len(training_data)} matches")
    print(f"File: {output_file}")
    
    # İstatistikler
    results = df['FTR'].value_counts()
    print(f"\nResults distribution:")
    print(f"  Home wins: {results.get('H', 0)} ({results.get('H', 0)/len(df)*100:.1f}%)")
    print(f"  Draws: {results.get('D', 0)} ({results.get('D', 0)/len(df)*100:.1f}%)")
    print(f"  Away wins: {results.get('A', 0)} ({results.get('A', 0)/len(df)*100:.1f}%)")
    
    return training_data

def update_team_stats_from_history(training_data):
    """
    Geçmiş verilerden takım istatistiklerini güncelle
    """
    print("\nUpdating team statistics from historical data...")
    
    teams_file = 'data/teams.json'
    
    try:
        with open(teams_file, 'r', encoding='utf-8') as f:
            teams = json.load(f)
    except:
        teams = {}
    
    # Her takım için istatistikleri hesapla
    team_stats = {}
    
    for match in training_data:
        home = match['home_team']
        away = match['away_team']
        
        # Takımları başlat
        if home not in team_stats:
            team_stats[home] = {
                'goals_scored': 0,
                'goals_conceded': 0,
                'matches': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0
            }
        
        if away not in team_stats:
            team_stats[away] = {
                'goals_scored': 0,
                'goals_conceded': 0,
                'matches': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0
            }
        
        # İstatistikleri güncelle
        team_stats[home]['goals_scored'] += match['home_goals']
        team_stats[home]['goals_conceded'] += match['away_goals']
        team_stats[home]['matches'] += 1
        
        team_stats[away]['goals_scored'] += match['away_goals']
        team_stats[away]['goals_conceded'] += match['home_goals']
        team_stats[away]['matches'] += 1
        
        # Sonuçları kaydet
        if match['result'] == 'H':
            team_stats[home]['wins'] += 1
            team_stats[away]['losses'] += 1
        elif match['result'] == 'D':
            team_stats[home]['draws'] += 1
            team_stats[away]['draws'] += 1
        else:
            team_stats[home]['losses'] += 1
            team_stats[away]['wins'] += 1
    
    # Takım istatistiklerini hesapla ve kaydet
    updated_count = 0
    
    for team_name, stats in team_stats.items():
        if stats['matches'] > 0:
            attack = stats['goals_scored'] / stats['matches']
            defense = stats['goals_conceded'] / stats['matches']
            
            # Form hesapla (son performans)
            win_rate = stats['wins'] / stats['matches']
            form = win_rate
            
            # ELO hesapla (basit)
            elo = 1500 + (win_rate - 0.5) * 400
            
            # Normalize edilmiş isim
            from ai.models.team_engine import normalize
            team_key = normalize(team_name)
            
            teams[team_key] = {
                'attack': round(attack, 4),
                'defense': round(defense, 4),
                'form': round(form, 4),
                'elo': round(elo, 2),
                'matches': stats['matches']
            }
            updated_count += 1
    
    # Kaydet
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    
    print(f"Updated {updated_count} teams")
    print(f"Total teams in database: {len(teams)}")
    
    return teams

if __name__ == "__main__":
    # Geçmiş verileri indir
    df = download_historical_data(start_year=2015, end_year=2025)
    
    if df is not None:
        # Eğitim verisini hazırla
        training_data = prepare_training_data(df)
        
        # Takım istatistiklerini güncelle
        teams = update_team_stats_from_history(training_data)
        
        print("\n✓ Historical data processing complete!")
