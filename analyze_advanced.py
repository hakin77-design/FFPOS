import json
from collections import defaultdict

print("ADVANCED MATCH ANALYSIS")
print("=" * 60)

all_matches = []
for file in ["data/football_json_matches.json", "data/historical_matches.json", "data/european_matches.json", "data/mackolik_matches.json"]:
    try:
        with open(file) as f:
            m = json.load(f)
            all_matches.extend(m)
            print(f"Loaded {len(m)} from {file}")
    except:
        pass

print(f"Total: {len(all_matches)}")

team_stats = defaultdict(lambda: {"hm":0,"am":0,"hw":0,"hd":0,"hl":0,"aw":0,"ad":0,"al":0,"hgs":0,"hgc":0,"ags":0,"agc":0,"tm":0})

valid = 0
for m in all_matches:
    try:
        h = m.get("home_team") or m.get("home")
        a = m.get("away_team") or m.get("away")
        hs = m.get("home_score")
        as_ = m.get("away_score")
        if not h or not a or hs is None or as_ is None:
            continue
        hs, as_ = int(hs), int(as_)
        team_stats[h]["hm"] += 1
        team_stats[h]["tm"] += 1
        team_stats[h]["hgs"] += hs
        team_stats[h]["hgc"] += as_
        if hs > as_: team_stats[h]["hw"] += 1
        elif hs == as_: team_stats[h]["hd"] += 1
        else: team_stats[h]["hl"] += 1
        team_stats[a]["am"] += 1
        team_stats[a]["tm"] += 1
        team_stats[a]["ags"] += as_
        team_stats[a]["agc"] += hs
        if as_ > hs: team_stats[a]["aw"] += 1
        elif as_ == hs: team_stats[a]["ad"] += 1
        else: team_stats[a]["al"] += 1
        valid += 1
    except:
        continue

print(f"Valid: {valid}, Teams: {len(team_stats)}")

enhanced = {}
for team, s in team_stats.items():
    if s["tm"] < 5:
        continue
    hwr = s["hw"] / max(s["hm"], 1)
    hag = s["hgs"] / max(s["hm"], 1)
    hac = s["hgc"] / max(s["hm"], 1)
    awr = s["aw"] / max(s["am"], 1)
    aag = s["ags"] / max(s["am"], 1)
    aac = s["agc"] / max(s["am"], 1)
    tg = s["hgs"] + s["ags"]
    tc = s["hgc"] + s["agc"]
    agpm = tg / s["tm"]
    acpm = tc / s["tm"]
    att = min(100, (agpm / 2.5) * 100)
    def_ = min(100, max(0, (1 - acpm / 2.5) * 100))
    ha = hag / max(aag, 0.5)
    tw = s["hw"] + s["aw"]
    wr = tw / s["tm"]
    form = min(100, wr * 100)
    elo = 1500 + (wr - 0.5) * 500 + (agpm - acpm) * 100
    enhanced[team] = {"name":team,"matches":s["tm"],"attack":round(att,1),"defense":round(def_,1),"form":round(form,1),"elo":round(elo,1),"home_win_rate":round(hwr,3),"away_win_rate":round(awr,3),"home_avg_goals":round(hag,2),"away_avg_goals":round(aag,2),"home_avg_conceded":round(hac,2),"away_avg_conceded":round(aac,2),"home_advantage":round(ha,2),"avg_goals_per_match":round(agpm,2)}

with open("data/teams.json", "w") as f:
    json.dump(enhanced, f, indent=2)

print(f"Enhanced: {len(enhanced)} - Saved!")
for t in sorted(enhanced.values(), key=lambda x: x["matches"], reverse=True)[:5]:
    print(f"{t['name']}: {t['matches']}m ATT:{t['attack']} DEF:{t['defense']} ELO:{t['elo']}")
