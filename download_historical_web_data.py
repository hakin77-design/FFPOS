import requests
import json
import os
import csv
from io import StringIO
from datetime import datetime

# football-data.co.uk - Free historical data source
# Covers 2010-2025 for major European leagues
LEAGUES = {
    'E0': 'English Premier League',
    'E1': 'English Championship',
    'SP1': 'Spanish La Liga',
    'I1': 'Italian Serie A',
    'D1': 'German Bundesliga',
    'F1': 'French Ligue 1',
    'N1': 'Dutch Eredivisie',
    'P1': 'Portuguese Liga',
    'T1': 'Turkish Super Lig',
    'G1': 'Greek Super League'
}

# Seasons from 2010 to 2025
SEASONS = [
    '1011', '1112', '1213', '1314', '1415', '1516', 
    '1617', '1718', '1819', '1920', '2021', '2122', 
    '2223', '2324', '2425'
]

def normalize_team_name(name):
    \
