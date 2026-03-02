import json
import torch
import torch.nn as nn

print("=== Merging All Data Sources ===\n")

# Load all data
with open("data/mackolik_matches.json") as f:
    mackolik = json.load(f)
print(f"Mackolik: {len(mackolik):,}")

with open("data/historical_matches.json") as f:
    historical = json.load(f)
print(f"RapidAPI: {len(historical):,}")

with open("data/final_dataset_matches.json") as f:
    final_ds = json.load(f)
print(f"Final Dataset: {len(final_ds):,}")

with open("data/sports_skills_all_matches.json") as f:
    sports_skills = json.load(f)
print(f"sports-skills: {len(sports_skills):,}")

# Merge all
all_data = mackolik + historical + final_ds + sports_skills
print(f"\nTotal before dedup: {len(all_data):,}")

# Remove duplicates
seen = set()
unique = []

for m in all_data:
    key = (m["date"], m["home_team"].lower(), m["away_team"].lower(), m["home_score"], m["away_score"])
    if key not in seen:
        seen.add(key)
        unique.append(m)

print(f"Unique matches: {len(unique):,}")

# Update team statistics
print("\nRecalculating team stats...")

def normalize(name):
    import unicodedata
    name = unicodedata.normalize("NFKD", name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

stats = {}
for m in unique:
    h = normalize(m["home_team"])
    a = normalize(m["away_team"])
    hs = m["home_score"]
    as_ = m["away_score"]
    
    for t in [h, a]:
        if t not in stats:
            stats[t] = {"scored": 0, "conceded": 0, "matches": 0, "wins": 0}
    
    stats[h]["scored"] += hs
    stats[h]["conceded"] += as_
    stats[h]["matches"] += 1
    stats[a]["scored"] += as_
    stats[a]["conceded"] += hs
    stats[a]["matches"] += 1
    
    if hs > as_:
        stats[h]["wins"] += 1
    elif hs < as_:
        stats[a]["wins"] += 1

teams = {}
for key, s in stats.items():
    if s["matches"] < 3:
        continue
    
    avg_s = s["scored"] / s["matches"]
    avg_c = s["conceded"] / s["matches"]
    wr = s["wins"] / s["matches"]
    
    attack = min(100, max(10, avg_s * 50))
    defense = min(100, max(10, 100 - (avg_c * 30)))
    form = min(100, max(10, wr * 100))
    elo = max(1100, min(1900, 1500 + (wr - 0.5) * 400))
    
    teams[key] = {
        "attack": round(attack, 2),
        "defense": round(defense, 2),
        "form": round(form, 2),
        "elo": round(elo, 2),
        "matches": s["matches"]
    }

with open("data/teams.json", "w") as f:
    json.dump(teams, f, indent=2)

print(f"Teams: {len(teams):,}")

# Prepare training data
print("\nPreparing training data...")
X_train = []
y_train = []

for m in unique:
    h = normalize(m["home_team"])
    a = normalize(m["away_team"])
    
    if h not in teams or a not in teams:
        continue
    
    hs = teams[h]
    as_ = teams[a]
    
    features = [
        hs["attack"] / 100.0,
        hs["defense"] / 100.0,
        hs["form"] / 100.0,
        (hs["elo"] - 1000) / 1000.0,
        as_["attack"] / 100.0,
        as_["defense"] / 100.0,
        as_["form"] / 100.0,
        (as_["elo"] - 1000) / 1000.0
    ]
    
    home_score = m["home_score"]
    away_score = m["away_score"]
    
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

print(f"Training samples: {len(X_train):,}")
print(f"  Home wins: {(y_train == 0).sum().item():,}")
print(f"  Draws: {(y_train == 1).sum().item():,}")
print(f"  Away wins: {(y_train == 2).sum().item():,}")

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
print(f"\nDevice: {device}")

model = FootballPredictor().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

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
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs}] Loss: {avg_loss:.4f} Accuracy: {accuracy:.2f}%")
    
    if avg_loss < best_loss:
        best_loss = avg_loss

print(f"\nTraining completed!")
print(f"  Best loss: {best_loss:.4f}")
print(f"  Final accuracy: {accuracy:.2f}%")

torch.save(model.state_dict(), "ai_model.pt")
print(f"\nModel saved to ai_model.pt")

# Verification
print("\n=== Verification ===")
strong = [0.9, 0.9, 0.9, 0.4]
weak = [0.3, 0.3, 0.3, -0.4]

test_X = torch.FloatTensor([[
    strong[0], strong[1], strong[2], strong[3],
    weak[0], weak[1], weak[2], weak[3]
]]).to(device)

model.eval()
with torch.no_grad():
    output = model(test_X)
    probs = torch.softmax(output, dim=1)[0].cpu().numpy()
    
    print(f"Strong Home vs Weak Away:")
    print(f"  Home: {probs[0]*100:.1f}%  Draw: {probs[1]*100:.1f}%  Away: {probs[2]*100:.1f}%")
    
    if probs[0] > probs[2]:
        print("  ✓ CORRECT!")

print(f"\n✅ Model trained with {len(unique):,} matches!")
print(f"   (Mackolik + RapidAPI + Final Dataset + sports-skills)")
