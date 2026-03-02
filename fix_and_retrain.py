import torch
import torch.nn as nn
import json
import numpy as np

print("=== Fixing Model Training ===")
print("Problem: Labels were reversed!")
print()

# Load data
with open("data/mackolik_matches.json") as f:
    mackolik_matches = json.load(f)
print(f"✓ Mackolik: {len(mackolik_matches):,} matches")

with open("data/historical_matches.json") as f:
    rapidapi_matches = json.load(f)
print(f"✓ RapidAPI: {len(rapidapi_matches):,} matches")

with open("data/teams.json") as f:
    teams_data = json.load(f)
print(f"✓ Teams: {len(teams_data):,} teams")

all_matches = mackolik_matches + rapidapi_matches
print(f"\n✓ Total: {len(all_matches):,} matches")

def normalize_team(name):
    if not name:
        return ""
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

# Prepare training data with CORRECT labels
print("\nPreparing training data with CORRECT labels...")
X_train = []
y_train = []

for match in all_matches:
    home_key = normalize_team(match["home_team"])
    away_key = normalize_team(match["away_team"])
    
    if home_key not in teams_data or away_key not in teams_data:
        continue
    
    home_stats = teams_data[home_key]
    away_stats = teams_data[away_key]
    
    # Features
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
    
    # CORRECT Label mapping:
    # Output[0] = home win probability
    # Output[1] = draw probability  
    # Output[2] = away win probability
    home_score = match["home_score"]
    away_score = match["away_score"]
    
    if home_score > away_score:
        label = 0  # Home win -> index 0
    elif home_score < away_score:
        label = 2  # Away win -> index 2
    else:
        label = 1  # Draw -> index 1
    
    X_train.append(features)
    y_train.append(label)

X_train = torch.FloatTensor(X_train)
y_train = torch.LongTensor(y_train)

print(f"✓ Training samples: {len(X_train):,}")
print(f"  Label 0 (Home wins): {(y_train == 0).sum().item():,}")
print(f"  Label 1 (Draws): {(y_train == 1).sum().item():,}")
print(f"  Label 2 (Away wins): {(y_train == 2).sum().item():,}")

# Model
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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n✓ Device: {device}")

model = FootballPredictor().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training
print("\nTraining with CORRECT labels...")
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

# Save
torch.save(model.state_dict(), "ai_model.pt")
print(f"\n✓ Model saved to ai_model.pt")

# Verification test
print("\n=== Verification Test ===")
print("Testing with known strong vs weak teams...")

# Create test case: Strong home team vs weak away team
strong_features = [0.9, 0.9, 0.9, 0.4]  # High attack, defense, form, elo
weak_features = [0.3, 0.3, 0.3, -0.4]   # Low attack, defense, form, elo

test_X = torch.FloatTensor([[
    strong_features[0], strong_features[1], strong_features[2], strong_features[3],
    weak_features[0], weak_features[1], weak_features[2], weak_features[3]
]]).to(device)

model.eval()
with torch.no_grad():
    output = model(test_X)
    probs = torch.softmax(output, dim=1)[0].cpu().numpy()
    
    print(f"Strong Home vs Weak Away:")
    print(f"  Home Win: {probs[0]*100:.1f}%")
    print(f"  Draw: {probs[1]*100:.1f}%")
    print(f"  Away Win: {probs[2]*100:.1f}%")
    
    if probs[0] > probs[2]:
        print("  ✓ CORRECT: Home team favored!")
    else:
        print("  ✗ ERROR: Still predicting wrong!")

# Test reverse
test_X2 = torch.FloatTensor([[
    weak_features[0], weak_features[1], weak_features[2], weak_features[3],
    strong_features[0], strong_features[1], strong_features[2], strong_features[3]
]]).to(device)

with torch.no_grad():
    output2 = model(test_X2)
    probs2 = torch.softmax(output2, dim=1)[0].cpu().numpy()
    
    print(f"\nWeak Home vs Strong Away:")
    print(f"  Home Win: {probs2[0]*100:.1f}%")
    print(f"  Draw: {probs2[1]*100:.1f}%")
    print(f"  Away Win: {probs2[2]*100:.1f}%")
    
    if probs2[2] > probs2[0]:
        print("  ✓ CORRECT: Away team favored!")
    else:
        print("  ✗ ERROR: Still predicting wrong!")

print("\n✅ Model retrained with correct labels!")
