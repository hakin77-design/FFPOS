import torch
import torch.nn as nn
import json
import numpy as np
from datetime import datetime

print("=== FFPAS Model Training ===")
print("148K+ Mackolik Data + RapidAPI Data")
print()

# Load all data
print("Loading data...")
with open("data/mackolik_matches.json") as f:
    mackolik_matches = json.load(f)
print(f"✓ Mackolik: {len(mackolik_matches):,} matches")

with open("data/historical_matches.json") as f:
    rapidapi_matches = json.load(f)
print(f"✓ RapidAPI: {len(rapidapi_matches):,} matches")

with open("data/teams.json") as f:
    teams_data = json.load(f)
print(f"✓ Teams: {len(teams_data):,} teams")

# Combine all matches
all_matches = mackolik_matches + rapidapi_matches
print(f"\n✓ Total: {len(all_matches):,} matches for training")

def normalize_team(name):
    if not name:
        return ""
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

# Prepare training data
print("\nPreparing training data...")
X_train = []
y_train = []

for match in all_matches:
    home_key = normalize_team(match["home_team"])
    away_key = normalize_team(match["away_team"])
    
    if home_key not in teams_data or away_key not in teams_data:
        continue
    
    home_stats = teams_data[home_key]
    away_stats = teams_data[away_key]
    
    # Features: [home_attack, home_defense, home_form, home_elo, 
    #            away_attack, away_defense, away_form, away_elo]
    features = [
        home_stats["attack"] / 100.0,
        home_stats["defense"] / 100.0,
        home_stats["form"] / 100.0,
        (home_stats["elo"] - 1000) / 1000.0,
        away_stats["attack"] / 100.0,
        away_stats["defense"] / 100.0,
        away_stats["form"] / 100.0,
        (away_stats["elo"] - 1000) / 1000.0
    ]
    
    # Label: 0=home win, 1=draw, 2=away win
    home_score = match["home_score"]
    away_score = match["away_score"]
    
    if home_score > away_score:
        label = 0
    elif home_score < away_score:
        label = 2
    else:
        label = 1
    
    X_train.append(features)
    y_train.append(label)

X_train = torch.FloatTensor(X_train)
y_train = torch.LongTensor(y_train)

print(f"✓ Training samples: {len(X_train):,}")
print(f"  Home wins: {(y_train == 0).sum().item():,}")
print(f"  Draws: {(y_train == 1).sum().item():,}")
print(f"  Away wins: {(y_train == 2).sum().item():,}")

# Define model
class FootballPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(8, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 3)
        )
    
    def forward(self, x):
        return self.net(x)

# Initialize model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n✓ Device: {device}")

model = FootballPredictor().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training
print("\nTraining model...")
batch_size = 512
epochs = 50

X_train = X_train.to(device)
y_train = y_train.to(device)

best_loss = float("inf")
for epoch in range(epochs):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    # Mini-batch training
    for i in range(0, len(X_train), batch_size):
        batch_X = X_train[i:i+batch_size]
        batch_y = y_train[i:i+batch_size]
        
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += batch_y.size(0)
        correct += (predicted == batch_y).sum().item()
    
    avg_loss = total_loss / (len(X_train) / batch_size)
    accuracy = 100 * correct / total
    
    if (epoch + 1) % 5 == 0:
        print(f"Epoch [{epoch+1}/{epochs}] Loss: {avg_loss:.4f} Accuracy: {accuracy:.2f}%")
    
    if avg_loss < best_loss:
        best_loss = avg_loss

print(f"\n✓ Training completed!")
print(f"  Best loss: {best_loss:.4f}")
print(f"  Final accuracy: {accuracy:.2f}%")

# Save model
torch.save(model.state_dict(), "ai_model.pt")
print(f"\n✓ Model saved to ai_model.pt")

# Test predictions
print("\n=== Sample Predictions ===")
model.eval()
with torch.no_grad():
    sample_X = X_train[:5]
    sample_y = y_train[:5]
    outputs = model(sample_X)
    probs = torch.softmax(outputs, dim=1)
    _, predicted = torch.max(outputs, 1)
    
    for i in range(5):
        actual = ["Home Win", "Draw", "Away Win"][sample_y[i].item()]
        pred = ["Home Win", "Draw", "Away Win"][predicted[i].item()]
        prob = probs[i].cpu().numpy()
        print(f"  Actual: {actual:10s} | Predicted: {pred:10s} | Probs: H:{prob[0]:.2f} D:{prob[1]:.2f} A:{prob[2]:.2f}")

print("\n✅ Model training complete with 148K+ matches!")
