from ai.models.goals_predictor import predict_goals
from ai.models.ensemble import predict

print('=== GOALS PREDICTION TEST ===\n')

test_matches = [
    ('Manchester City', 'Liverpool'),
    ('Barcelona', 'Real Madrid'),
    ('Bayern Munich', 'Borussia Dortmund'),
    ('Juventus', 'Inter Milan'),
    ('PSG', 'Marseille'),
    ('Arsenal', 'Chelsea')
]

print('Match                                    Result Pred    Goals Predictions')
print('-' * 85)

for home, away in test_matches:
    # Match result
    result_pred = predict(home, away)
    h = int(result_pred['home'] * 100)
    d = int(result_pred['draw'] * 100)
    a = int(result_pred['away'] * 100)
    
    # Goals prediction
    goals_pred = predict_goals(home, away)
    
    print(f'{home:20s} vs {away:15s}  H:{h:2d}% D:{d:2d}% A:{a:2d}%  ', end='')
    print(f'0.5:{int(goals_pred["over_0.5"]*100):2d}%  1.5:{int(goals_pred["over_1.5"]*100):2d}%  2.5:{int(goals_pred["over_2.5"]*100):2d}%  3.5:{int(goals_pred["over_3.5"]*100):2d}%')

print('\n✓ Goals prediction working!')
