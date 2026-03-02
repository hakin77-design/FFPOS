import requests
import json
import os
from datetime import datetime

# DataHub.io'dan indirilecek ligler
LEAGUES = {
    'english-premier-league': 'Premier League',
    'spanish-la-liga': 'La Liga',
    'italian-serie-a': 'Serie A',
    'german-bundesliga': 'Bundesliga',
    'french-ligue-1': 'Ligue 1'
}

def download_league_data(league_id, league_name):
    print(f'Downloading {league_name}...')
    
    # DataHub.io API endpoint
    url = f'https://datahub.io/core/{league_id}/datapackage.json'
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        package = response.json()
        
        all_matches = []
        
        # Her sezon için CSV dosyalarını bul
        for resource in package.get('resources', []):
            if resource.get('format') == 'csv' and 'season' in resource.get('name', ''):
                csv_url = resource.get('path')
                if not csv_url.startswith('http'):
                    csv_url = f'https://datahub.io/core/{league_id}/{csv_url}'
                
                print(f'  Fetching {resource.get(\
