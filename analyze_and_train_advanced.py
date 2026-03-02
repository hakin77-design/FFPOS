import json
import math
from collections import defaultdict

print("=" * 80)
print("ADVANCED MATCH ANALYSIS AND TRAINING")
print("=" * 80)

# Load all match data
all_matches = []
data_files = [
    "data/football_json_matches.json",
    "data/historical_matches.json",
    "data/european_matches.json",
    "data/mackolik_matches.json",
    "data/final_dataset_matches.json",
    "data/data_raw_matches.json"
]

for file in data_files:
    try:
        with open(file) as f:
            matches = json.load(f)
            all_matches.extend(matches)
            print(f"Loaded {len(matches)} matches from {file}")
    except:
        pass

print(f"\nTotal matches loaded: {len(all_matches)}")

# Analyze team statistics
team_stats = defaultdict(lambda: {
    "home_matches": 0,
    "away_matches": 0,
    "home_wins": 0,
    "home_draws": 0,
    "home_losses": 0,
    "away_wins": 0,
    "away_draws": 0,
    "away_losses": 0,
    "home_goals_scored": 0,
    "home_goals_conceded": 0,
    "away_goals_scored": 0,
    "away_goals_conceded": 0,
    "ht_home_goals": 0,
    "ht_away_goals": 0,
    "total_matches": 0
})

valid_matches = 0
for match in all_matches:
    try:
        home = match.get("home_team") or match.get("home")
        away = match.get("away_team") or match.get("away")
        home_score = match.get("home_score")
        away_score = match.get("away_score")

        if not home or not away or home_score is None or away_score is None:
            continue

        home_score = int(home_score)
        away_score = int(away_score)

        # Home team stats
        team_stats[home]["home_matches"] += 1
        team_stats[home]["total_matches"] += 1
        team_stats[home]["home_goals_scored"] += home_score
        team_stats[home]["home_goals_conceded"] += away_score

        if home_score > away_score:
            team_stats[home]["home_wins"] += 1
        elif home_score == away_score:
            team_stats[home]["home_draws"] += 1
        else:
            team_stats[home]["home_losses"] += 1

        # Away team stats
        team_stats[away]["away_matches"] += 1
        team_stats[away]["total_matches"] += 1
        team_stats[away]["away_goals_scored"] += away_score
        team_stats[away]["away_goals_conceded"] += home_score

        if away_score > home_score:
            team_stats[away]["away_wins"] += 1
        elif away_score == home_score:
            team_stats[away]["away_draws"] += 1
        else:
            team_stats[away]["away_losses"] += 1
        
        # Half-time stats if available
        ht_home = match.get("ht_home_score")
        ht_away = match.get("ht_away_score")
        if ht_home is not None and ht_away is not None:
            team_stats[home]["ht_home_goals"] += int(ht_home)
            team_stats[away]["ht_away_goals"] += int(ht_away)

        valid_matches += 1

    except:
        continue

print(f"Valid matches analyzed: {valid_matches}")
print(f"Unique teams: {len(team_stats)}")

# Calculate advanced metrics for each team
enhanced_teams = {}
for team, stats in team_stats.items():
    if stats["total_matches"] < 5:
        continue

    # Home performance
    home_win_rate = stats["home_wins"] / max(stats["home_matches"], 1)
    home_avg_goals = stats["home_goals_scored"] / max(stats["home_matches"], 1)
    home_avg_conceded = stats["home_goals_conceded"] / max(stats["home_matches"], 1)

    # Away performance
    away_win_rate = stats["away_wins"] / max(stats["away_matches"], 1)
    away_avg_goals = stats["away_goals_scored"] / max(stats["away_matches"], 1)
    away_avg_conceded = stats["away_goals_conceded"] / max(stats["away_matches"], 1)

    # Overall metrics
    total_goals = stats["home_goals_scored"] + stats["away_goals_scored"]
    total_conceded = stats["home_goals_conceded"] + stats["away_goals_conceded"]
    avg_goals_per_match = total_goals / stats["total_matches"]
    avg_conceded_per_match = total_conceded / stats["total_matches"]

    # Attack and defense ratings (0-100)
    attack_rating = min(100, (avg_goals_per_match / 2.5) * 100)
    defense_rating = min(100, max(0, (1 - avg_conceded_per_match / 2.5) * 100))

    # Home advantage factor
    home_advantage = home_avg_goals / max(away_avg_goals, 0.5)
    
    # Form (recent performance)
    total_wins = stats["home_wins"] + stats["away_wins"]
    win_rate = total_wins / stats["total_matches"]
    form_rating = min(100, win_rate * 100)

    # ELO-like rating
    elo = 1500 + (win_rate - 0.5) * 500 + (avg_goals_per_match - avg_conceded_per_match) * 100

    enhanced_teams[team] = {
        "name": team,
        "matches": stats["total_matches"],
        "attack": round(attack_rating, 1),
        "defense": round(defense_rating, 1),
        "form": round(form_rating, 1),
        "elo": round(elo, 1),
        "home_win_rate": round(home_win_rate, 3),
        "away_win_rate": round(away_win_rate, 3),
        "home_avg_goals": round(home_avg_goals, 2),
        "away_avg_goals": round(away_avg_goals, 2),
        "home_avg_conceded": round(home_avg_conceded, 2),
        "away_avg_conceded": round(away_avg_conceded, 2),
        "home_advantage": round(home_advantage, 2),
        "avg_goals_per_match": round(avg_goals_per_match, 2)
    }

print(f"\nEnhanced teams with stats: {len(enhanced_teams)}")

# Save enhanced team data
with open("data/teams.json", "w") as f:
    json.dump(enhanced_teams, f, indent=2)

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"Teams updated: {len(enhanced_teams)}")

avg_matches = sum(t['matches'] for t in enhanced_teams.values()) / len(enhanced_teams)
print(f"Average matches per team: {avg_matches:.1f}")

# Show sample teams
print("\nSample enhanced teams:")
sample_teams = sorted(enhanced_teams.values(), key=lambda x: x['matches'], reverse=True)[:5]
for team in sample_teams:
    team_name = team['name']
    print(f"\n{team_name}:")
    print(f"  Matches: {team['matches']}")
    print(f"  Attack: {team['attack']}, Defense: {team['defense']}, Form: {team['form']}")
    print(f"  ELO: {team['elo']}")
    print(f"  Home: {team['home_avg_goals']} goals/match, Win rate: {team['home_win_rate']*100:.1f}%")
    print(f"  Away: {team['away_avg_goals']} goals/match, Win rate: {team['away_win_rate']*100:.1f}%")
    print(f"  Home advantage: {team['home_advantage']:.2f}x")

print("\nTeam data saved to data/teams.json")
