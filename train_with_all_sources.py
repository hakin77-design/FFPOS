import torch
import json
import random
from ai.models.team_engine import find_team, normalize

print('=== TRAINING WITH ALL DATA ===\n')

# Load teams
print('1. Loading teams...')
with open('data/teams.json', 'r', encoding='utf-8') as f:
    teams_data = json.load(f)
print(f'   Total teams: {len(teams_data)}')

# Load all match sources
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

# Prepare training data
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
        
        # Label: 0=Home, 1=Draw, 2=Away
        result = match['result']
        if result == 'H':
            label = 0
        elif result == 'D':
            label = 1
        else:  # 'A'
            label = 2
        
        X_train.append(features)
        y_train.append(label)

print(f'   Training samples: {len(X_train)}')

# Convert to tensors
X = torch.FloatTensor(X_train)
y = torch.LongTensor(y_train)

# Shuffle
indices = list(range(len(X)))
random.shuffle(indices)
X = X[indices]
y = y[indices]

# Model
class FootballPredictor(torch.nn.Module):
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
            torch.nn.Linear(64, 3)
        )
    
    def forward(self, x):
        return self.net(x)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'\n4. Training on {device}...')

model = FootballPredictor().to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

batch_size = 256
epochs = 50

X = X.to(device)
y = y.to(device)

for epoch in range(epochs):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for i in range(0, len(X), batch_size):
        batch_X = X[i:i+batch_size]
        batch_y = y[i:i+batch_size]
        
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += batch_y.size(0)
        correct += (predicted == batch_y).sum().item()
    
    if (epoch + 1) % 10 == 0:
        accuracy = 100 * correct / total
        print(f'   Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(X):.4f}, Accuracy: {accuracy:.2f}%')

# Save model
torch.save(model.state_dict(), 'ai_model.pt')
print('\n✓ Model saved to ai_model.pt')

# Final test
model.eval()
with torch.no_grad():
    test_size = min(1000, len(X))
    outputs = model(X[:test_size])
    _, predicted = torch.max(outputs.data, 1)
    accuracy = (predicted == y[:test_size]).sum().item() / test_size
    print(f'✓ Final test accuracy ({test_size} samples): {accuracy*100:.2f}%')
