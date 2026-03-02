import json
import unicodedata

def normalize(name):
    if not name:
        return ""
    name = unicodedata.normalize("NFKD", name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    return name.lower().replace(" ", "").replace("-", "").replace(".", "")

with open("data/teams.json") as f:
    old_teams = json.load(f)

new_teams = {}
for key, value in old_teams.items():
    new_key = normalize(key)
    if new_key in new_teams:
        # Merge if duplicate
        old_val = new_teams[new_key]
        new_teams[new_key] = {
            "attack": (old_val["attack"] + value["attack"]) / 2,
            "defense": (old_val["defense"] + value["defense"]) / 2,
            "form": (old_val["form"] + value["form"]) / 2,
            "elo": (old_val["elo"] + value["elo"]) / 2,
            "matches": old_val["matches"] + value["matches"]
        }
    else:
        new_teams[new_key] = value

with open("data/teams.json", "w") as f:
    json.dump(new_teams, f, indent=2)

print(f"Normalized {len(old_teams)} -> {len(new_teams)} teams")
