import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

class BetDiaryScraper:
    def __init__(self):
        self.base_url = 'https://betdiary.io'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9'
        })
    
    def get_matches(self):
        \
