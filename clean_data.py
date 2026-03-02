import json
from collections import defaultdict

print("=== Cleaning Data ===")

with open("data/mackolik_matches.json") as f:
    mackolik = json.load(f)
with open("data/historical_matches.json") as f:
    historical = json.load(f)
with open("data/final_dataset_matches.json") as f:
    final_ds = json.load(f)

all_matches = mackolik + historical + final_ds
print(f"Total: {len(all_matches):,}")

seen = set()
unique = []
dups = 0

for m in all_matches:
    key = (m["date"], m["home_team"].lower(), m["away_team"].lower(), m["home_score"], m["away_score"])
    if key not in seen:
        seen.add(key)
        unique.append(m)
    else:
        dups += 1

print(f"Duplicates: {dups:,}")
print(f"Unique: {len(unique):,}")

def normalize(name):
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
print("Done!")
