import torch
import torch.nn as nn
import json
import random
import numpy as np


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 3),
            nn.Softmax(dim=1)
        )
    
    def forward(self, x):
        return self.net(x)


def load_teams():
    with open("data/teams.json", "r", encoding="utf-8") as f:
        return json.load(f)


def generate_training_data(teams, num_samples=5000):
    team_list = list(teams.items())
    X = []
    y = []
    
    for _ in range(num_samples):
        home_name, home_data = random.choice(team_list)
        away_name, away_data = random.choice(team_list)
        
        features = [
            home_data.get("attack", 1.0),
            max(home_data.get("defense", 1.0), 0.1),  # Min 0.1
            0.5,
            away_data.get("attack", 1.0),
            max(away_data.get("defense", 1.0), 0.1),  # Min 0.1
            0.5,
            1500,
            1500,
            0,
            0
        ]
        
        home_attack = home_data.get("attack", 1.0)
        home_defense = max(home_data.get("defense", 1.0), 0.1)
        away_attack = away_data.get("attack", 1.0)
        away_defense = max(away_data.get("defense", 1.0), 0.1)
        
        # Daha gerçekçi hesaplama
        home_strength = (home_attack / away_defense) * 1.2  # Ev sahibi avantajı
        away_strength = away_attack / home_defense
        draw_factor = 0.8
        
        total = home_strength + away_strength + draw_factor
        
        prob_home = home_strength / total
        prob_draw = draw_factor / total
        prob_away = away_strength / total
        
        X.append(features)
        y.append([prob_home, prob_draw, prob_away])
    
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)


def train_model():
    print("Loading teams...")
    teams = load_teams()
    print(f"Loaded {len(teams)} teams")
    
    print("\nGenerating training data...")
    X_train, y_train = generate_training_data(teams, num_samples=10000)
    print(f"Generated {len(X_train)} training samples")
    
    print("\nInitializing model...")
    model = Net()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    print("\nTraining model...")
    epochs = 100
    batch_size = 64
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        indices = torch.randperm(len(X_train))
        
        for i in range(0, len(X_train), batch_size):
            batch_indices = indices[i:i+batch_size]
            batch_X = X_train[batch_indices]
            batch_y = y_train[batch_indices]
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            avg_loss = total_loss / (len(X_train) / batch_size)
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
    
    print("\nSaving model...")
    torch.save(model.state_dict(), "ai_model.pt")
    print("Model saved to ai_model.pt")
    
    print("\nTesting model...")
    model.eval()
    with torch.no_grad():
        test_sample = X_train[0].unsqueeze(0)
        prediction = model(test_sample)
        print(f"Sample prediction: Home={prediction[0][0]:.3f}, Draw={prediction[0][1]:.3f}, Away={prediction[0][2]:.3f}")
    
    print("\n✅ Training complete!")


if __name__ == "__main__":
    train_model()
