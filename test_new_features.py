from ai.models.ensemble import predict
from ai.models.confidence import calculate_confidence
from ai.auto_analyze import predict_from_odds
from ai.models.team_engine import find_team, normalize

print('=== TESTING NEW FEATURES ===\n')

# Test 1: Confidence Scores
print('1. CONFIDENCE SCORES TEST')
print('-' * 60)

test_matches = [
    ('Manchester City', 'Liverpool', 2.5, 3.5, 2.8),
    ('Barcelona', 'Real Madrid', 2.2, 3.3, 3.4),
    ('Unknown Team A', 'Unknown Team B', 2.0, 3.0, 4.0)
]

for home, away, h_odds, d_odds, a_odds in test_matches:
    pred = predict(home, away)
    odds_pred = predict_from_odds(h_odds, d_odds, a_odds)
    
    # Get team data
    home_team = find_team(normalize(home))
    away_team = find_team(normalize(away))
    team_data = None
    if home_team and away_team:
        team_data = {
            "home_matches": home_team.get("matches", 0),
            "away_matches": away_team.get("matches", 0)
        }
    
    conf = calculate_confidence(pred, odds_pred, team_data)
    
    h, d, a = int(pred['home']*100), int(pred['draw']*100), int(pred['away']*100)
    print(f'{home:20s} vs {away:20s}')
    print(f'  Prediction: H:{h}% D:{d}% A:{a}%')
    print(f'  Confidence: {conf["confidence"]:.1f}% ({conf["level"]})')
    print(f'  Factors: {conf["factors"]}')
    print()

# Test 2: Cache
print('\n2. CACHE TEST')
print('-' * 60)
from ai.utils.cache import get_cache

cache = get_cache()
print(f'Initial stats: {cache.stats()}')

# Cache some predictions
cache.set('Team A', 'Team B', {'home': 0.5, 'draw': 0.3, 'away': 0.2})
cache.set('Team C', 'Team D', {'home': 0.4, 'draw': 0.3, 'away': 0.3})

# Try to retrieve
result = cache.get('Team A', 'Team B')
print(f'Cache hit: {result}')

result = cache.get('Team X', 'Team Y')
print(f'Cache miss: {result}')

print(f'Final stats: {cache.stats()}')

# Test 3: Accuracy Tracker
print('\n3. ACCURACY TRACKER TEST')
print('-' * 60)
from ai.utils.accuracy_tracker import get_tracker

tracker = get_tracker()

# Log a prediction
tracker.log_prediction(
    'Test Home', 'Test Away',
    {'home': 0.5, 'draw': 0.3, 'away': 0.2},
    {'home': 2.0, 'draw': 3.0, 'away': 4.0},
    {'confidence': 75, 'level': 'High'}
)

# Update with result
tracker.update_result('Test Home', 'Test Away', 'H')

stats = tracker.get_stats()
print(f'Accuracy stats: {stats}')

print('\n✓ All features tested successfully!')
