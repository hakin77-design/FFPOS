import requests

print('=' * 80)
print('FINAL GOALS PREDICTION TEST')
print('=' * 80)

response = requests.get('http://localhost:8010/api/matches?min_confidence=40')
matches = response.json()

print(f'\nFetched {len(matches)} matches with confidence >= 40%\n')

for i, match in enumerate(matches[:5], 1):
    home = match['home']
    away = match['away']
    league = match['league']
    pred = match['prediction']
    goals = match['goals']
    conf = match['confidence']
    
    print(f'{i}. {home} vs {away}')
    print(f'   League: {league}')
    h = int(pred['home']*100)
    d = int(pred['draw']*100)
    a = int(pred['away']*100)
    print(f'   Prediction: H:{h}% D:{d}% A:{a}%')
    
    g05 = int(goals['over_0.5']*100)
    g15 = int(goals['over_1.5']*100)
    g25 = int(goals['over_2.5']*100)
    g35 = int(goals['over_3.5']*100)
    print(f'   Goals: 0.5:{g05}% 1.5:{g15}% 2.5:{g25}% 3.5:{g35}%')
    print(f'   Confidence: {conf[\
