import torch
import json
import random
from ai.models.team_engine import find_team, normalize

print('=== TRAINING GOALS PREDICTION MODEL ===\n')

# Load teams
print('1. Loading teams...')
with open('data/teams.json', 'r', encoding='utf-8') as f:
    teams_data = json.load(f)
print(f'   Total teams: {len(teams_data)}')

# Load match data
print('\n2. Loading match data...')
match_sources = [
    ('data/european_matches.json', 'European'),
    ('data/football_json_matches.json', 'Football.json')
]

all_matches = []
for file_path, source_name in match_sources:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            matches = json.load(f)
        all_matches.extend(matches)
        print(f'   {source_name}: {len(matches)} matches')
    except:
        print(f'   {source_name}: Not found')

print(f'   Total matches: {len(all_matches)}')

# Prepare training data for goals prediction
print('\n3. Preparing training data...')
X_train = []
y_train = []

for match in all_matches:
    home = find_team(normalize(match['home']))
    away = find_team(normalize(match['away']))
    
    if home and away:
        features = [
            home.get('attack', 50) / 100.0,
            home.get('defense', 50) / 100.0,
            home.get('form', 50) / 100.0,
            (home.get('elo', 1500) - 1000) / 1000.0,
            away.get('attack', 50) / 100.0,
            away.get('defense', 50) / 100.0,
            away.get('form', 50) / 100.0,
            (away.get('elo', 1500) - 1000) / 1000.0
        ]
        
        # Calculate total goals
        total_goals = match['home_goals'] + match['away_goals']
        
        # Labels: [over_0.5, over_1.5, over_2.5, over_3.5]
        labels = [
            1.0 if total_goals > 0.5 else 0.0,
            1.0 if total_goals > 1.5 else 0.0,
            1.0 if total_goals > 2.5 else 0.0,
            1.0 if total_goals > 3.5 else 0.0
        ]
        
        X_train.append(features)
        y_train.append(labels)

print(f'   Training samples: {len(X_train)}')

# Convert to tensors
X = torch.FloatTensor(X_train)
y = torch.FloatTensor(y_train)

# Shuffle
indices = list(range(len(X)))
random.shuffle(indices)
X = X[indices]
y = y[indices]

# Model
class GoalsPredictor(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(8, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(64, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(64, 4)
        )
    
    def forward(self, x):
        return self.net(x)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'\n4. Training on {device}...')

model = GoalsPredictor().to(device)
criterion = torch.nn.BCEWithLogitsLoss()  # Binary cross-entropy for multi-label
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

batch_size = 256
epochs = 50

X = X.to(device)
y = y.to(device)

for epoch in range(epochs):
    model.train()
    total_loss = 0
    
    for i in range(0, len(X), batch_size):
        batch_X = X[i:i+batch_size]
        batch_y = y[i:i+batch_size]
        
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    if (epoch + 1) % 10 == 0:
        # Calculate accuracy
        model.eval()
        with torch.no_grad():
            test_outputs = torch.sigmoid(model(X[:1000]))
            test_preds = (test_outputs > 0.5).float()
            accuracy = (test_preds == y[:1000]).float().mean().item() * 100
        print(f'   Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(X):.4f}, Accuracy: {accuracy:.2f}%')

# Save model
torch.save(model.state_dict(), 'goals_model.pt')
print('\n✓ Model saved to goals_model.pt')

# Test predictions
print('\n5. Testing predictions...')
model.eval()
test_matches = [
    ('Manchester City', 'Liverpool'),
    ('Barcelona', 'Real Madrid'),
    ('Bayern Munich', 'Borussia Dortmund')
]

for home, away in test_matches:
    home_team = find_team(normalize(home))
    away_team = find_team(normalize(away))
    
    if home_team and away_team:
        features = torch.FloatTensor([
            home_team.get('attack', 50) / 100.0,
            home_team.get('defense', 50) / 100.0,
            home_team.get('form', 50) / 100.0,
            (home_team.get('elo', 1500) - 1000) / 1000.0,
            away_team.get('attack', 50) / 100.0,
            away_team.get('defense', 50) / 100.0,
            away_team.get('form', 50) / 100.0,
            (away_team.get('elo', 1500) - 1000) / 1000.0
        ]).unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = torch.sigmoid(model(features))[0].cpu().numpy()
        
        print(f'{home} vs {away}:')
        print(f'  Over 0.5: {output[0]*100:.0f}%  Over 1.5: {output[1]*100:.0f}%  Over 2.5: {output[2]*100:.0f}%  Over 3.5: {output[3]*100:.0f}%')

print('\n✓ Training complete!')
