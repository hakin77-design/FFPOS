#!/usr/bin/env python3
"""
Retrain FFPAS AI Model with Data-Raw Dataset
"""
import json
import torch
import torch.nn as nn
from collections import defaultdict
from datetime import datetime

print('=' * 60)
print('FFPAS MODEL RETRAINING WITH DATA-RAW')
print('=' * 60)

# Load data
print('Loading data...')
with open('data/data_raw_matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

with open('data/teams.json', 'r', encoding='utf-8') as f:
    teams = json.load(f)

print(f'Loaded {len(matches)} matches and {len(teams)} teams')

# Prepare training data
print('Preparing training data...')
X_train, y_train = [], []

def normalize(name):
    return name.lower().strip()

for match in matches:
    home_key = normalize(match['home_team'])
    away_key = normalize(match['away_team'])
    
    if home_key not in teams or away_key not in teams:
        continue
    
    home_team = teams[home_key]
    away_team = teams[away_key]
    
    # Features: attack, defense, form, elo for both teams
    features = [
        home_team.get('attack', 50) / 100,
        home_team.get('defense', 50) / 100,
        home_team.get('form', 50) / 100,
        home_team.get('elo', 1500) / 2500,
        away_team.get('attack', 50) / 100,
        away_team.get('defense', 50) / 100,
        away_team.get('form', 50) / 100,
        away_team.get('elo', 1500) / 2500
    ]
    
    # Label: 0=home win, 1=draw, 2=away win
    hs, as_ = match['home_score'], match['away_score']
    if hs > as_:
        label = 0
    elif hs == as_:
        label = 1
    else:
        label = 2
    
    X_train.append(features)
    y_train.append(label)

print(f'Prepared {len(X_train)} training samples')

# Convert to tensors
X = torch.tensor(X_train, dtype=torch.float32)
y = torch.tensor(y_train, dtype=torch.long)

# Define model
class FootballPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(8, 64)
        self.fc2 = nn.Linear(64, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 3)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

print('Initializing model...')
model = FootballPredictor()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training
print('Training model...')
epochs = 50
batch_size = 256

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
    
    accuracy = 100 * correct / total
    avg_loss = total_loss / (len(X) / batch_size)
    
    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%')

# Save model
print('Saving model...')
torch.save(model.state_dict(), 'ai_model_data_raw.pt')
print('Model saved to ai_model_data_raw.pt')

# Test predictions
print('Testing predictions...')
model.eval()
with torch.no_grad():
    test_sample = X[:10]
    predictions = model(test_sample)
    probs = torch.softmax(predictions, dim=1)
    print('Sample predictions (Home/Draw/Away):')
    for i, prob in enumerate(probs[:5]):
        print(f'  Match {i+1}: {prob[0]:.2f} / {prob[1]:.2f} / {prob[2]:.2f}')

print('=' * 60)
print('TRAINING COMPLETED!')
print('=' * 60)
