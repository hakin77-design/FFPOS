import json

with open("data/teams.json") as f:
    teams = json.load(f)

search_terms = ["manchester", "bayern", "real", "madrid"]

print("Searching for teams:")
for term in search_terms:
    found = [k for k in teams.keys() if term in k]
    print(f"\n{term}:")
    for k in found[:5]:
        print(f"  {k}")
