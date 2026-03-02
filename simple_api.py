#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random

# Load teams data
with open('data/teams.json', 'r', encoding='utf-8') as f:
    teams_data = json.load(f)

def normalize_team(name):
    return name.lower().strip()

def predict_match(home_team, away_team, home_odds, draw_odds, away_odds):
    home_key = normalize_team(home_team)
    away_key = normalize_team(away_team)
    
    # Get team stats
    home_stats = teams_data.get(home_key, {
        'attack': 50, 'defense': 50, 'form': 50, 'elo': 1500
    })
    away_stats = teams_data.get(away_key, {
        'attack': 50, 'defense': 50, 'form': 50, 'elo': 1500
    })
    
    # Simple prediction based on stats
    home_strength = (home_stats.get('attack', 50) + home_stats.get('form', 50)) / 2
    away_strength = (away_stats.get('attack', 50) + away_stats.get('form', 50)) / 2
    
    # Add home advantage
    home_strength *= 1.15
    
    total = home_strength + away_strength
    home_prob = home_strength / total
    away_prob = away_strength / total
    draw_prob = 0.25
    
    # Normalize
    total_prob = home_prob + draw_prob + away_prob
    home_prob /= total_prob
    draw_prob /= total_prob
    away_prob /= total_prob
    
    # Goals prediction
    avg_goals = (home_stats.get('avg_goals_per_match', 1.5) + away_stats.get('avg_goals_per_match', 1.5)) / 2
    
    return {
        'home': round(home_prob, 2),
        'draw': round(draw_prob, 2),
        'away': round(away_prob, 2)
    }, {
        'over_0.5': 0.85,
        'over_1.5': 0.70,
        'over_2.5': 0.50,
        'over_3.5': 0.30
    }

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/matches':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Generate sample matches
            sample_matches = [
                {
                    'home': 'Arsenal', 'away': 'Liverpool',
                    'league': 'Premier League',
                    'odds_home': 2.10, 'odds_draw': 3.40, 'odds_away': 3.20
                },
                {
                    'home': 'Barcelona', 'away': 'Real Madrid',
                    'league': 'La Liga',
                    'odds_home': 2.50, 'odds_draw': 3.20, 'odds_away': 2.80
                },
                {
                    'home': 'Bayern Munich', 'away': 'Borussia Dortmund',
                    'league': 'Bundesliga',
                    'odds_home': 1.80, 'odds_draw': 3.60, 'odds_away': 4.20
                }
            ]
            
            results = []
            for match in sample_matches:
                prediction, goals = predict_match(
                    match['home'], match['away'],
                    match['odds_home'], match['odds_draw'], match['odds_away']
                )
                
                # Calculate value
                value_home = max(0, (prediction['home'] * match['odds_home'] - 1) * 100)
                value_draw = max(0, (prediction['draw'] * match['odds_draw'] - 1) * 100)
                value_away = max(0, (prediction['away'] * match['odds_away'] - 1) * 100)
                
                results.append({
                    'home': match['home'],
                    'away': match['away'],
                    'league': match['league'],
                    'odds_home': match['odds_home'],
                    'odds_draw': match['odds_draw'],
                    'odds_away': match['odds_away'],
                    'prediction': prediction,
                    'halftime': {
                        'home': round(prediction['home'] * 0.7, 2),
                        'draw': round(prediction['draw'] * 1.2, 2),
                        'away': round(prediction['away'] * 0.7, 2)
                    },
                    'goals': goals,
                    'top_scores': [
                        {'score': '2-1', 'probability': 0.12},
                        {'score': '1-1', 'probability': 0.11},
                        {'score': '2-0', 'probability': 0.10}
                    ],
                    'value': {
                        'home': {'value': round(value_home, 2)},
                        'draw': {'value': round(value_draw, 2)},
                        'away': {'value': round(value_away, 2)}
                    },
                    'confidence': {
                        'confidence': random.randint(65, 85),
                        'level': 'High'
                    }
                })
            
            self.wfile.write(json.dumps(results).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[API] {format % args}")

if __name__ == '__main__':
    port = 5000
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f'FFPAS API Server running on http://localhost:{port}')
    print(f'Endpoint: http://localhost:{port}/api/matches')
    print(f'Teams loaded: {len(teams_data)}')
    server.serve_forever()
