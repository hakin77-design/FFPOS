from ai.models.ensemble import predict

print('=== TESTING WITH UPDATED MODEL ===\n')

test_matches = [
    # Premier League
    ('Manchester United', 'Liverpool', 'Premier League'),
    ('Arsenal', 'Chelsea', 'Premier League'),
    ('Manchester City', 'Tottenham', 'Premier League'),
    
    # La Liga
    ('Barcelona', 'Real Madrid', 'La Liga'),
    ('Atletico Madrid', 'Sevilla', 'La Liga'),
    
    # Bundesliga
    ('Bayern Munich', 'Borussia Dortmund', 'Bundesliga'),
    
    # Serie A
    ('Juventus', 'Inter Milan', 'Serie A'),
    ('AC Milan', 'Napoli', 'Serie A'),
    
    # Ligue 1
    ('PSG', 'Marseille', 'Ligue 1'),
    
    # South American
    ('Boca Juniors', 'River Plate', 'Argentina')
]

for home, away, league in test_matches:
    pred = predict(home, away)
    h = int(pred['home'] * 100)
    d = int(pred['draw'] * 100)
    a = int(pred['away'] * 100)
    print(f'{home:20s} vs {away:20s} ({league:15s}) H:{h:2d}% D:{d:2d}% A:{a:2d}%')
